"""Repackage documentation additions and verify archived bytes; never run design code."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1] / 'work/csaw-github/fresh-clone'
PACKAGE = REPO / 'submission'
ORIGINAL = Path('/Users/al-zayedal-hassan/Documents/CSAW_Qwen_Submission_20261113T001822Z_9sj2k3k6/package/submission')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def inventory(root, excluded=()):
    result = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if '.git' in path.relative_to(root).parts or relative in excluded:
            continue
        if path.is_symlink():
            raise ValueError('Unexpected symlink: ' + relative)
        if path.is_file():
            data = path.read_bytes()
            result[relative] = {'bytes': len(data), 'sha256': sha(data)}
    return result

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')

def main():
    before = json.loads((HERE / 'BEFORE.json').read_text())
    originals = inventory(ORIGINAL)
    assert len(originals) == 262
    for name, entry in originals.items():
        assert sha((PACKAGE / name).read_bytes()) == entry['sha256'], name
        assert entry['sha256'] == before['original_files'][name], name
    sealed_zip = ORIGINAL.parent / 'submission.zip'
    assert sha(sealed_zip.read_bytes()) == '0c053f3595079dbe7aa11789e69b1e26d359619b7af72d7535d1da004ce0ca83'
    pinned = json.loads((PACKAGE / 'SOURCE_HASHES.json').read_text())
    assert all(sha((PACKAGE / name).read_bytes()) == digest for name, digest in pinned.items())
    pub = json.loads((PACKAGE / 'PUBLICATION_MANIFEST.json').read_text())
    pub['scope'] = 'Original tested package plus documentation, authentic log-recovery supplements and notices; self-excluding; no design changes or rerun.'
    pub['files'] = inventory(PACKAGE, ('PUBLICATION_MANIFEST.json',))
    write_json(PACKAGE / 'PUBLICATION_MANIFEST.json', pub)
    package_files = inventory(PACKAGE)
    archive = REPO / 'submission.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in package_files:
            info = zipfile.ZipInfo('submission/' + name, (2026, 11, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, (PACKAGE / name).read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(set(z.namelist())) == len(package_files)
        assert all(sha(z.read('submission/' + name)) == data['sha256'] for name, data in package_files.items())
    digest = sha(archive.read_bytes())
    (REPO / 'submission.zip.sha256').write_text(digest + '  submission.zip\n')
    checks = {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'source_base_commit': before['base_commit'],
        'original_files_byte_identical': len(originals),
        'frozen_source_files_byte_identical': len(pinned),
        'original_sealed_archive_unchanged': True,
        'archive_sha256': digest, 'archive_bytes': archive.stat().st_size,
        'archive_files': len(package_files), 'archive_crc_pass': True,
        'archive_matches_directory': True,
        'design_code_changed': False, 'design_code_executed': False,
        'new_simulations_claimed': False, 'published_solutions_used': False,
        'scope': 'Documentation and authentic-record supplementation; upload receipt is recorded after push.'
    }
    checks_dir = REPO / 'publication/nov12-documentation-update'
    checks_dir.mkdir(exist_ok=True)
    write_json(checks_dir / 'INTEGRATION_CHECKS.json', checks)
    current = inventory(REPO, ('REPOSITORY_MANIFEST.json',))
    repository_manifest = {
        'scope': 'Repository files except self-excluding manifest and Git metadata; byte integrity only. All original simulation-package files unchanged.',
        'files': [{'path': name, **entry} for name, entry in current.items()]
    }
    write_json(REPO / 'REPOSITORY_MANIFEST.json', repository_manifest)
    write_json(HERE / 'INTEGRATION_CHECKS.json', checks)
    print(json.dumps(checks, indent=2))

if __name__ == '__main__':
    main()
