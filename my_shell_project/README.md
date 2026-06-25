# my_shell — A Toy Unix Shell in C

A minimal but feature-rich Unix shell written from scratch in C. Based on Stephen Brennan's tutorial ["Write a Shell in C"](https://brennan.io/2015/01/16/write-a-shell-in-c/), then extended with original features.

## Build

```bash
gcc -Wall -Wextra -o my_shell my_shell.c
./my_shell
```

## Tutorial Features (Baseline)

- **Read-Parse-Execute loop** — the fundamental shell lifecycle
- **Dynamic line reading** — uses `getline()` for robust input handling
- **Tokenization** — splits input on whitespace with `strtok()`
- **Process launching** — `fork()` + `execvp()` + `waitpid()`
- **Built-in commands** — `cd`, `help`, `exit`

## Unique Extensions

| Feature | Description |
|---|---|
| **Persistent History** | Commands saved to `~/.my_shell_history` with duplicate suppression. |
| **`history` builtin** | Prints numbered command history. |
| **`!n` execution** | Re-runs the *n*th command from history. |
| **Colorized Prompt** | Shows `user:cwd$` in ANSI colors, with `~` shorthand for `$HOME`. |
| **`pwd` builtin** | Prints the current working directory. |
| **I/O Redirection** | `cmd > file`, `cmd >> file`, `cmd < file` |
| **Single Pipe** | `cmd1 \| cmd2` — creates a pipe, forks twice, wires stdout→stdin. |
| **Environment Expansion** | `$HOME`, `$USER`, `$PATH`, etc. are substituted before execution. |

The source code is heavily commented with notes on failed attempts and why the final approach was chosen (e.g., redirection must happen in the child process, not the parent).

## Example Session

```
$ ./my_shell
my_shell started. Type 'help' for features.
matteodimario:~/my_shell_project$ echo hello world
hello world
matteodimario:~/my_shell_project$ echo test > /tmp/demo.txt
matteodimario:~/my_shell_project$ cat < /tmp/demo.txt
test
matteodimario:~/my_shell_project$ ls | wc -l
3
matteodimario:~/my_shell_project$ history
  1  echo hello world
  2  echo test > /tmp/demo.txt
  3  cat < /tmp/demo.txt
  4  ls | wc -l
  5  history
matteodimario:~/my_shell_project$ !1
hello world
matteodimario:~/my_shell_project$ echo $HOME
/home/matteodimario
matteodimario:~/my_shell_project$ exit
```

## Limitations

- No quoting or backslash escaping
- Only a single pipe (`cmd1 | cmd2`), no chains
- No job control (`fg`, `bg`, `&`)
- No globbing (`*`, `?`)
