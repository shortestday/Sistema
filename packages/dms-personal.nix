{
  runCommand,
  python3,
  dms-shell,
}:
runCommand "dms-shell-personal-${dms-shell.version}"
  {
    pname = "dms-shell-personal";
    inherit (dms-shell) version meta;
    nativeBuildInputs = [ python3 ];
  }
  ''
    cp -a ${dms-shell}/. "$out"
    chmod -R u+w "$out/share/quickshell/dms"
    python3 ${../scripts/patch-dms.py} "$out/share/quickshell/dms" ${../desktop/dms-es.json}
    chmod u+w "$out/bin/dms" "$out/lib/systemd/user/dms.service"
    substituteInPlace "$out/bin/dms" \
      --replace-fail '${dms-shell}/share/quickshell/dms' "$out/share/quickshell/dms"
    substituteInPlace "$out/lib/systemd/user/dms.service" \
      --replace-fail '${dms-shell}/bin/dms' "$out/bin/dms"
  ''
