# pTock

A digital clock for the terminal, inspired by [tty-clock][0] and [tock][1].
The main difference with this version is that it is written in Python, and my goal was primarily to learn as much as possible about the language itself.

Note: emulating all the features of tty-clock and tock is **not** a goal of this project.

## Features

- Efficient bitmap and diff-based drawing.
- Timezone fetched fro mthe system using the **timedatectl** command [2].
- Military time and second display toggling.
- Color customization.
- Positioned or centered clock.
- Adjustable display size.
- Synchronization with system clock seconds.
- Do not require any particular Python library, only standard Python libs.
- If the terminal size changed, it will adjusts the clock position automatically.

## Installation and Dependencies

1. The only requirement is to have Python 3 installed and the basic core libraries.

2. It is already available in PyPi, so you only need to run pip to intall and ptock to start the clock, as below:

```sh
pip install python3-ptock
```

```sh
ptock -h
```

## Usage

```output
Usage: ptock [OPTIONS]

A digital clock for the terminal.

Options:
  -h, --help             show this help message and exit.
  -x, --x <X>            Horizontal 0-indexed position of top-left corner [default: 0].
  -y, --y <Y>            Vertical 0-indexed position of top-left corner [default: 0].
  -W, --width <WIDTH>    Font width in characters per tile [default: 2].
  -H, --height <HEIGHT>  Font height in characters per tile [default: 1].
  -s, --second           Display seconds.
  -m, --military         Display military (24-hour) time.
  -c, --center           Center the clock in the terminal. Overrides manual positioning.
  -C, --color <COLOR>    Change the color of the time [If none is given, random from 1 to 7].
  -v, --version          Show program's version number and exit.
```

Available commands with this feature flag set are:

- `q` or `Q` or `<ESC>`: Exit.
- `s`: Toggle second display.
- `m`: Toggle military (24H) time.
- `c`: Center the clock in the terminal.
- `0`..=`7`: Change to corresponding ANSI color.

## References

- [The timedatectl man page][2]

[0]: https://github.com/xorg62/tty-clock
[1]: https://github.com/nwtnni/tock
[2]: https://man7.org/linux/man-pages/man1/timedatectl.1.html
