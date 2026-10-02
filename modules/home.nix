{ pkgs, host, ... }:
let
  desk = pkgs.writeShellApplication {
    name = "desk";
    runtimeInputs = with pkgs; [
      coreutils
      jq
      curl
      git
      nixos-rebuild
      nssTools
      python3
    ];
    text = builtins.readFile ../scripts/desk.sh;
  };
in
{
  home-manager.useGlobalPkgs = true;
  home-manager.useUserPackages = true;
  home-manager.backupFileExtension = "hm-backup";
  home-manager.users.${host.username} = { lib, ... }: {
    home.stateVersion = "26.05";
    home.username = host.username;
    home.homeDirectory = "/home/${host.username}";
    home.packages = [ desk ];
    programs.bash.enable = true;
    programs.fish = {
      enable = true;
      shellAliases.aplicar-sistema = "cd ~/Sistema && desk apply";
    };
    programs.direnv.enable = true;
    programs.direnv.nix-direnv.enable = true;
    programs.git.enable = true;
    xdg.enable = true;
    xdg.userDirs = {
      enable = true;
      createDirectories = true;
    };
    xdg.mimeApps = {
      enable = true;
      defaultApplications = {
        "text/html" = [ "brave-browser.desktop" ];
        "x-scheme-handler/http" = [ "brave-browser.desktop" ];
        "x-scheme-handler/https" = [ "brave-browser.desktop" ];
        "application/pdf" = [ "org.gnome.Evince.desktop" ];
        "image/avif" = [ "org.gnome.Loupe.desktop" ];
        "image/bmp" = [ "org.gnome.Loupe.desktop" ];
        "image/gif" = [ "org.gnome.Loupe.desktop" ];
        "image/jpeg" = [ "org.gnome.Loupe.desktop" ];
        "image/png" = [ "org.gnome.Loupe.desktop" ];
        "image/svg+xml" = [ "org.gnome.Loupe.desktop" ];
        "image/tiff" = [ "org.gnome.Loupe.desktop" ];
        "image/webp" = [ "org.gnome.Loupe.desktop" ];
      };
    };
    xdg.configFile."niri/config.kdl".source = ../desktop/niri.kdl;
    xdg.configFile."ghostty/config".text = ''
      font-family = JetBrainsMono Nerd Font
      font-size = 11
      background = 181d20
      foreground = e3e6e3
      cursor-color = 94b9a8
      window-padding-x = 10
      window-padding-y = 10
      confirm-close-surface = true
    '';
    gtk = {
      enable = true;
      theme = {
        name = "Adwaita-dark";
        package = pkgs.gnome-themes-extra;
      };
      iconTheme = {
        name = "Adwaita";
        package = pkgs.adwaita-icon-theme;
      };
    };
    dconf.settings."org/gnome/desktop/interface".color-scheme = "prefer-dark";

    # These applications write their own settings. Seed once; never overwrite edits.
    home.activation.personalDefaults = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
      run ${pkgs.python3}/bin/python3 ${../scripts/seed.py} \
        --home "$HOME" --defaults ${../desktop/dms.json} \
        --agents ${../docs/AGENTS-global.md} --study ${../docs/AGENTS-study.md}
    '';
    xdg.desktopEntries = {
      pi = {
        name = "Pi";
        exec = "ghostty -e desk pi";
        icon = "utilities-terminal";
        categories = [ "Development" ];
      };
      firefox-lab = {
        name = "Firefox · Lab";
        exec = "desk lab %U";
        icon = "firefox";
        categories = [ "Network" ];
      };
      burp = {
        name = "Burp Suite";
        exec = "burpsuite";
        icon = "applications-development";
        categories = [ "Development" ];
      };
      estudio = {
        name = "Retomar estudio";
        exec = "ghostty -e desk study";
        icon = "accessories-text-editor";
        categories = [ "Education" ];
      };
      sistema = {
        name = "Configurar mi sistema con Pi";
        exec = "ghostty -e desk system";
        icon = "preferences-system";
        categories = [ "Settings" ];
      };
      bienvenida = {
        name = "Primeros pasos";
        exec = "ghostty -e desk welcome";
        icon = "help-browser";
        categories = [ "System" ];
      };
      chuleta = {
        name = "Chuleta del sistema";
        exec = "ghostty -e desk chuleta";
        icon = "help-browser";
        categories = [ "System" ];
      };
    };
    # Swayidle's before-sleep hook holds logind's delay inhibitor while locking.
    systemd.user.services.personal-idle = {
      Unit = {
        Description = "Bloqueo de pantalla e inactividad";
        After = [
          "graphical-session.target"
          "dms.service"
        ];
        PartOf = [ "graphical-session.target" ];
      };
      Service = {
        ExecStart = "${pkgs.swayidle}/bin/swayidle -w timeout 600 '${pkgs.dms-shell}/bin/dms ipc call lock lock' before-sleep '${pkgs.dms-shell}/bin/dms ipc call lock lock'";
        Restart = "on-failure";
      };
      Install.WantedBy = [ "graphical-session.target" ];
    };
  };
}
