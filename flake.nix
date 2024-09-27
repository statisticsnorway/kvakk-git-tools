{
  description = "kvakk-git-tools dev env";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin"];
      perSystem = {
        pkgs,
        lib,
        ...
      }: {
        devShells.default = pkgs.mkShell {
          name = "ssb-project-cli";
          packages =
            (with pkgs; [
              nixd
              python310
              python311
              python312
              python311Packages.ruff-lsp
              (poetry.override {python3 = python312;})
            ])
            ++ lib.optionals pkgs.stdenv.isDarwin (with pkgs.darwin.apple_sdk.frameworks; [
              Cocoa
              CoreServices
            ]);
        };

        formatter = pkgs.alejandra;
      };
    };
}
