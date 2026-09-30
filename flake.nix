{
  description = "Portatil personal: NixOS, Niri, DMS y agentes";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    disko = {
      url = "github:nix-community/disko";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    llm-agents.url = "github:numtide/llm-agents.nix";
    lanzaboote = {
      url = "github:nix-community/lanzaboote/v1.2.0";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs =
    inputs@{
      self,
      nixpkgs,
      home-manager,
      disko,
      ...
    }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
      # Keep the agents' own dependency set, matching their upstream binary cache.
      agentPkgs = import inputs.llm-agents.inputs.nixpkgs {
        inherit system;
        config.allowUnfree = true;
        overlays = [ inputs.llm-agents.overlays.shared-nixpkgs ];
      };
      host = builtins.fromJSON (builtins.readFile ./host/settings.json);
    in
    {
      nixosConfigurations.elitebook = nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = {
          inherit host;
          agents = agentPkgs.llm-agents;
        };
        modules = [
          disko.nixosModules.disko
          inputs.lanzaboote.nixosModules.lanzaboote
          home-manager.nixosModules.home-manager
          ./host/hardware.nix
          ./modules/disk.nix
          ./modules/system.nix
          ./modules/secure-boot.nix
          ./modules/home.nix
        ];
      };
      packages.${system} = {
        installer-tools = pkgs.buildEnv {
          name = "personal-os-installer-tools";
          paths = with pkgs; [
            python3
            git
            util-linux
            cryptsetup
          ];
        };
        validation-tools = pkgs.buildEnv {
          name = "personal-os-validation-tools";
          paths = with pkgs; [
            python3
            shellcheck
            nixfmt
            niri
          ];
        };
      };
      checks.${system} = {
        niri-config =
          pkgs.runCommand "niri-config-valid"
            {
              nativeBuildInputs = [ pkgs.niri ];
            }
            ''
              niri validate -c ${./desktop/niri.kdl}
              touch $out
            '';
        installer-safety =
          pkgs.runCommand "installer-safety"
            {
              nativeBuildInputs = [ pkgs.python3 ];
            }
            ''
              export PYTHONDONTWRITEBYTECODE=1
              python3 -m unittest discover -s ${./.}/tests -v
              touch $out
            '';
        shell-scripts =
          pkgs.runCommand "shell-scripts-valid"
            {
              nativeBuildInputs = [ pkgs.shellcheck ];
            }
            ''
              shellcheck ${./install.sh}
              shellcheck --shell bash ${./scripts/desk.sh}
              touch $out
            '';
      };
    };
}
