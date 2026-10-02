{
  config,
  pkgs,
  host,
  agents,
  ...
}:
{
  system.stateVersion = "26.05";
  networking.hostName = host.hostname;
  networking.networkmanager.enable = true;
  networking.networkmanager.plugins = [ pkgs.networkmanager-openvpn ];
  networking.firewall.enable = true;
  services.tailscale.enable = true;
  services.openssh = {
    enable = true;
    openFirewall = true;
    settings = {
      PasswordAuthentication = true;
      PermitRootLogin = "no";
    };
  };
  time.timeZone = host.timezone;
  i18n.defaultLocale = host.locale;
  services.xserver.xkb.layout = host.keyboard;
  console.useXkbConfig = true;

  boot.loader.systemd-boot.enable = true;
  boot.loader.systemd-boot.configurationLimit = 10;
  boot.loader.systemd-boot.editor = false;
  boot.loader.efi.canTouchEfiVariables = true;
  hardware.cpu.intel.updateMicrocode = true;
  hardware.enableRedistributableFirmware = true;
  hardware.graphics.enable = true;
  hardware.bluetooth.enable = true;
  hardware.bluetooth.powerOnBoot = false;
  zramSwap.enable = true;
  services.btrfs.autoScrub.enable = true;

  nix.settings.experimental-features = [
    "nix-command"
    "flakes"
  ];
  nix.settings.auto-optimise-store = true;
  nix.settings.max-jobs = 2;
  nix.settings.cores = 2;
  # Explicit upstream cache: no global trust escalation for the user or agent.
  nix.settings.extra-substituters = [ "https://cache.numtide.com" ];
  nix.settings.extra-trusted-public-keys = [
    "niks3.numtide.com-1:DTx8wZduET09hRmMtKdQDxNNthLQETkc/yaX7M4qK0g="
  ];
  nixpkgs.config.allowUnfree = true;

  users.mutableUsers = true;
  users.users.root.initialHashedPassword = "!";
  users.users.${host.username} = {
    isNormalUser = true;
    description = host.username;
    extraGroups = [
      "wheel"
      "networkmanager"
      "video"
      "audio"
    ];
    initialHashedPassword = "!"; # Installer sets the password through stdin.
    shell = pkgs.fish;
  };
  security.sudo.wheelNeedsPassword = true;
  security.pam.services.sddm.enableGnomeKeyring = true;
  security.polkit.enable = true;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };
  services.upower.enable = true;
  services.power-profiles-daemon.enable = true;
  services.gvfs.enable = true;
  services.udisks2.enable = true;
  services.gnome.gnome-keyring.enable = true;

  programs.fish.enable = true;
  programs.niri.enable = true;
  programs.xwayland.enable = true;
  programs.dms-shell = {
    enable = true;
    package = pkgs.callPackage ../packages/dms-personal.nix { };
    systemd.enable = true;
    enableDynamicTheming = false;
    enableAudioWavelength = false;
    enableCalendarEvents = false;
    enableSystemMonitoring = false;
  };
  programs.firefox = {
    enable = true;
    policies.ExtensionSettings."foxyproxy@eric.h.jung" = {
      installation_mode = "force_installed";
      install_url = "https://addons.mozilla.org/firefox/downloads/latest/foxyproxy-standard/latest.xpi";
    };
  };
  services.displayManager.sddm = {
    enable = true;
    wayland.enable = true;
  };
  services.displayManager.defaultSession = "niri";

  environment.systemPackages = with pkgs; [
    ghostty
    brave
    burpsuite
    proton-pass
    proton-pass-cli
    tailscale
    libsecret
    nautilus
    loupe
    gnome-text-editor
    evince
    agents.pi
    agents.orca
    agents.zcode
    git
    curl
    wget
    jq
    ripgrep
    fd
    fzf
    bat
    yazi
    btop
    unzip
    zip
    openssh
    openvpn
    wireguard-tools
    mosh
    tmux
    rsync
    restic
    age
    python3
    uv
    direnv
    nix-direnv
    nixfmt
    nixd
    wl-clipboard
    brightnessctl
    networkmanagerapplet
    xwayland-satellite
    swayidle
    libnotify
  ];
  fonts.packages = with pkgs; [
    inter
    noto-fonts
    noto-fonts-color-emoji
    nerd-fonts.jetbrains-mono
  ];
  programs.dconf.enable = true;
  environment.etc."brave/policies/managed/personal.json".text = builtins.toJSON {
    BraveRewardsDisabled = true;
    BraveNewsDisabled = true;
    ExtensionInstallForcelist = [
      # Proton Pass: Free Password Manager
      "ghmbeldphafepmbegfdlkpapadhbakde;https://clients2.google.com/service/update2/crx"
    ];
  };
  environment.etc."personal-os.json".text = builtins.toJSON host;
}
