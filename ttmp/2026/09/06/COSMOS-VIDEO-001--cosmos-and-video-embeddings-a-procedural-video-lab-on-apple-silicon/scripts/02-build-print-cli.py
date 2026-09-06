"""Build the existing remote printer CLI without unsupported Linux BLE.

Go's build overlay leaves the Almanach checkout untouched. The temporary
binary fails explicitly for native BLE; HTTP remote printing is unchanged.
"""
import json, subprocess, tempfile
from pathlib import Path
repo=Path('/Users/manuel/code/wesen/go-go-golems/almanach')
with tempfile.TemporaryDirectory(prefix='cosmos-almanach-build-') as tmp:
 tmp=Path(tmp)
 stub=tmp/'native.go'
 stub.write_text('''package app
import (
 "context"
 "fmt"
 "github.com/go-go-golems/glazed/pkg/middlewares"
)
func runNativeBLEProvision(ctx context.Context, s *BLEProvisionSettings, gp middlewares.Processor, readPassphrase bool) error {
 return fmt.Errorf("native BLE is unavailable in this temporary macOS remote-print build")
}
''')
 overlay=tmp/'overlay.json'
 overlay.write_text(json.dumps({'Replace':{str(repo/'internal/app/cmd_ble_provision_native.go'):str(stub)}}))
 subprocess.run(['go','build','-overlay',str(overlay),'-o','/tmp/cosmos-almanach-render-service','./cmd/almanach-render-service'],cwd=repo,check=True)
