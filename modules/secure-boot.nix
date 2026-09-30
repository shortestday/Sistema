{
  lib,
  pkgs,
  host,
  ...
}:
let
  secureBoot = host.secureBoot or false;
  tpmUnlock = host.tpmUnlock or false;
in
{
  security.tpm2.enable = true;
  boot.initrd.systemd.enable = true;
  boot.initrd.systemd.tpm2.enable = true;

  # Keys are created on the HP after installation, never in the Nix store or Git.
  boot.loader.systemd-boot.enable = lib.mkIf secureBoot (lib.mkForce false);
  boot.lanzaboote = {
    enable = secureBoot;
    pkiBundle = "/var/lib/sbctl";
  };
  boot.initrd.luks.devices.cryptroot.crypttabExtraOpts = lib.optionals tpmUnlock [
    "tpm2-device=auto"
  ];

  assertions = [
    {
      assertion = !tpmUnlock || secureBoot;
      message = "El desbloqueo TPM de este sistema requiere el arranque firmado con Lanzaboote.";
    }
  ];

  environment.systemPackages = [
    pkgs.sbctl
    pkgs.tpm2-tools
    pkgs.cryptsetup
  ];
}
