# SDVCrosscompile

This pipeline will cross-compile a mod for Windows, Mac and Linux.

## Download

You can find a download [here](https://github.com/rumangerst/SDVCrosscompile/releases). Also you can just clone the whole repository.

## Configuration

SDVCrosscompile doesn't need any configuration to work. But you can
change settings like build parameters in `xcompile.py`.

## Usage

There are two ways to use SDVCrosscompile:

1. Extract it into the same folder as the \*.sln file
2. Extract it somewhere else and let it run in your project directory

### Running from command line

If you extracted SDVCrosscompile into the same folder as your solution, just open a command line and run `python xbuild.py` (Windows) or `./xbuild.py` (Linux/Mac).

### Integrate into your IDE

#### MonoDevelop

1. Open the project settings
2. Go to Build -> Custom Commands
3. Set the type of the custom command to "Custom Command"
4. Name it as you wish
5. Select `xcompile.sh` (Linux/Mac) or `xcompile.bat` as command
6. Set the working directory to the solution dir (`${SolutionDir}`)
7. You can find the command in the "Project" menu

![Screenshot](https://rumangerst.github.io/SDVCrosscompile/docs/monodevelop-setup.png)

### Visual Studio

1. Open Tools -> External Tools
2. Add a new tool
3. Set the title as you want
4. Select `xcompile.bat` as command
5. Set initial directory to the solution dir (`${SolutionDir}`)
6. If you don't want a separate CMD window, check "Use Output Window"

![Screenshot](https://rumangerst.github.io/SDVCrosscompile/docs/vs-setup.png)

### Command line parameters

You can customize the behavior of SDVCrosscompile with command line parameters:

Usage: `./xcompile[.bat|.sh|.py] [--no-silverplum] [--auto-silverplum] [--no-graphics] [--no-zip] [--keep-dependencies] [--output <output directory>] [--lib-<platform> <lib directory>] [--build-targetdir-<platform> <directory>] [--build-args-<platform> <arg1> <arg2> ...] [--sln <solution file 1> <solution file 2> ...]`

|Argument|Explanation|
|--------|-----------|
|`--sln` | Defines the solutions to be built. If not `--sln` is present, SDVCrosscompile will build all \*.sln files. |
|`--no-graphics` | Asks for input with CLI instead of dialogs |
|`--no-zip` | Disables automatic packing into archives. |
|`--keep-dependencies` | Keeps the depencies from the `lib-*` folders in the output directories.|
|`--output` | Sets the output directory. `%solution%` will be replaced with the solution name. Default is `xbuild_result_%solution%` |
|`--lib-<platform>` | Sets the directory containing the Windows build dependencies. Default is `lib-<platform>`. `<platform>` must be `windows`, `linux` or `mac`.|
|`--build-targetdir-<platform>` | Sets the directory containing the binaries. Relative to the project directory. Default is `bin/Release`. |
|`--build-args-<platform>` | Sets the arguments for `xbuild`. Default is `/p:DefineConstants=XCOMPILE /p:Configuration=Release`. |
|`--override-calling-platform` | Sets the current platform the script is running in. Must be `windows`, `linux` or `mac`. Case sensitive. |



## Requirements

* [Mono](http://www.mono-project.com/)
* [Python 3](https://www.python.org/). If you are using Windows, choose to add it to PATH.

### Projects

Your projects need to use the [Stardew ModBuildConfig package](https://www.nuget.org/packages/Pathoschild.Stardew.ModBuildConfig) to automatically resolve dependencies.
You can find more information about this in the [CanIMod Wiki](http://canimod.com/guides/crossplatforming-a-smapi-mod).

### Additional files
For SDVCrosscompile to work, you need to provide all dependency files for all systems
in `lib-windows`, `lib-linux` and `lib-mac` folders. Just copy all the files.
Linux and Mac are known to be compatible with each other, so just making a copy will suffice.

XNA libraries must be searched within the Windows directory. Use WINE on Linux or Mac.

If you download the binary distribution of this tool, the libraries will be included by default.

```
.
├── lib-linux
│   ├── Lidgren.Network.dll
│   ├── MonoGame.Framework.dll
│   ├── Newtonsoft.Json.dll
│   ├── StardewModdingAPI.exe
│   ├── StardewValley.exe
│   └── xTile.dll
├── lib-mac
│   ├── Lidgren.Network.dll
│   ├── MonoGame.Framework.dll
│   ├── Newtonsoft.Json.dll
│   ├── StardewModdingAPI.exe
│   ├── StardewValley.exe
│   └── xTile.dll
└── lib-windows
    ├── Lidgren.Network.dll
    ├── Microsoft.Xna.Framework.dll
    ├── Microsoft.Xna.Framework.Game.dll
    ├── Microsoft.Xna.Framework.Graphics.dll
    ├── Microsoft.Xna.Framework.Net.dll
    ├── Microsoft.Xna.Framework.Video.dll
    ├── Microsoft.Xna.Framework.Xact.dll
    ├── StardewModdingAPI.exe
    ├── Stardew Valley.exe
    └── xTile.dll
```
