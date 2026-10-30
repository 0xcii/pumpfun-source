#!/usr/bin/env python3
"""Generate analyst disassembly, never a source rebuild or candidate executable."""
import argparse,hashlib,json,os,pathlib,shutil,subprocess,tempfile
from analyze import program_names
ROOT=pathlib.Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('--objdump',type=pathlib.Path,required=True); ap.add_argument('--output',type=pathlib.Path,required=True); args=ap.parse_args()
if args.output.exists(): ap.error('output already exists')
# Read the tool once: the manifest hashes these bytes, so these exact bytes are what must run.
tool_bytes=args.objdump.read_bytes()
tool_sha256=hashlib.sha256(tool_bytes).hexdigest()
manifest={'tool_sha256':tool_sha256}
# Disassemble into a sibling staging directory so a failed run leaves no partial output behind.
args.output.parent.mkdir(parents=True,exist_ok=True)
# Plain mkdir, not mkdtemp: the rename below publishes this directory's mode.
staging=args.output.parent/f'.{args.output.name}.{os.getpid()}'; staging.mkdir()
try:
    with tempfile.TemporaryDirectory() as tmp:
        tool=pathlib.Path(tmp)/'objdump'
        def fresh_tool():
            # Re-materialize from the hashed bytes before every run: the bytes
            # that execute are the bytes the manifest records, even if a previous
            # execution replaced the file at this path.
            tool.write_bytes(tool_bytes); tool.chmod(0o555); return tool
        def checked_snapshot(path,sha256):
            # A snapshot that changed after its hash was recorded must fail the
            # run, never publish output under the recorded hash.
            if hashlib.sha256(path.read_bytes()).hexdigest()!=sha256: raise RuntimeError(f'{path.name} snapshot changed during the run')
        manifest['version']=subprocess.check_output([str(fresh_tool()),'--version'],text=True)
        manifest['outputs']={}
        for name in program_names():
            binary=ROOT/f'evidence/original/{name}/deployed.so'; target=staging/f'{name}.asm'
            # Read the input once: the manifest hashes these bytes, so these exact bytes are what must be disassembled.
            data=binary.read_bytes(); input_sha256=hashlib.sha256(data).hexdigest()
            snapshot=pathlib.Path(tmp)/f'{name}.so'; snapshot.write_bytes(data); snapshot.chmod(0o444)
            checked_snapshot(snapshot,input_sha256)
            with target.open('wb') as out: subprocess.run([str(fresh_tool()),'-d',str(snapshot)],stdout=out,check=True)
            manifest['outputs'][name]={'input_sha256':input_sha256,'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (staging/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    staging.rename(args.output)
except BaseException:
    shutil.rmtree(staging,ignore_errors=True); raise
