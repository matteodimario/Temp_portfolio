/*
 * my_shell.c - A minimal Unix shell written in C
 *
 * Based on Stephen Brennan's excellent tutorial:
 * https://brennan.io/2015/01/16/write-a-shell-in-c/
 *
 * I followed the tutorial to learn fork/exec/waitpid mechanics, then extended
 * it with my own features to explore shell internals more deeply.
 *
 * UNIQUE FEATURES ADDED (beyond the tutorial):
 *   1. Persistent command history  - ~/.my_shell_history, `history` builtin, `!n`
 *   2. Colorized prompt            - shows cwd + username in ANSI colors
 *   3. pwd builtin                 - mirrors bash's pwd
 *   4. I/O redirection             - `cmd > file` and `cmd < file`
 *   5. Single-pipe support         - `cmd1 | cmd2`
 *   6. Environment expansion       - `$HOME`, `$USER`, `$PATH`, etc.
 *
 * COMPILATION: gcc -Wall -Wextra -o my_shell my_shell.c
 */

#include <sys/wait.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <ctype.h>

/* ========================================================================
 * CONFIGURATION CONSTANTS
 * ======================================================================== */
#define LSH_RL_BUFSIZE 1024   /* Initial buffer size for reading lines */
#define LSH_TOK_BUFSIZE 64    /* Initial token array size */
#define LSH_TOK_DELIM " \t\r\n\a"
#define HISTORY_MAX 128       /* Max commands to remember in one session */
#define HISTORY_FILE ".my_shell_history"

/* ========================================================================
 * GLOBAL HISTORY STATE
 *
 * The tutorial stops at a very basic shell. I wanted to understand how
 * real shells (bash, zsh) remember what you typed, so I added a simple
 * in-memory history buffer plus persistent storage to ~/.my_shell_history.
 *
 * ATTEMPT 1: I first tried writing history after every command with fopen()
 *            in append mode. This worked but was slow and leaked the FILE*
 *            if the user hit Ctrl-C. I switched to buffering in memory and
 *            flushing only at exit or when history fills.
 * ATTEMPT 2: I tried using readline/history.h (GNU readline) but decided
 *            against it — this is a learning project, and outsourcing
 *            history to a library would defeat the purpose.
 * ======================================================================== */
static char *history[HISTORY_MAX];
static int history_count = 0;

/* ========================================================================
 * FUNCTION DECLARATIONS (forward declarations to break dependency cycles)
 * ======================================================================== */
int lsh_cd(char **args);
int lsh_help(char **args);
int lsh_exit(char **args);
int lsh_pwd(char **args);
int lsh_history(char **args);

/* ========================================================================
 * BUILTIN COMMAND TABLE
 *
 * The tutorial uses parallel arrays of names and function pointers.
 * This is a clean way to add builtins without a giant switch statement.
 * I extended the table with `pwd` and `history`.
 * ======================================================================== */
char *builtin_str[] = {
  "cd",
  "help",
  "exit",
  "pwd",
  "history"
};

int (*builtin_func[]) (char **) = {
  &lsh_cd,
  &lsh_help,
  &lsh_exit,
  &lsh_pwd,
  &lsh_history
};

int lsh_num_builtins(void) {
  return sizeof(builtin_str) / sizeof(char *);
}

/* ========================================================================
 * HISTORY HELPERS
 * ======================================================================== */

/*
 * get_history_path - Build the full path to ~/.my_shell_history
 *
 * I had to decide between storing history in the current directory (easy
 * but messy) or in the user's home. Real shells use $HOME, so I do too.
 */
static char *get_history_path(void) {
  const char *home = getenv("HOME");
  if (!home) home = ".";  /* fallback if HOME is unset */
  size_t len = strlen(home) + 1 + strlen(HISTORY_FILE) + 1;
  char *path = malloc(len);
  if (path) {
    snprintf(path, len, "%s/%s", home, HISTORY_FILE);
  }
  return path;
}

/*
 * load_history - Read previous session's history from disk on startup.
 *
 * NOTE: I only load the last HISTORY_MAX lines so the buffer never
 * overflows. A real shell would use a ring buffer or linked list.
 */
static void load_history(void) {
  char *path = get_history_path();
  if (!path) return;
  FILE *fp = fopen(path, "r");
  if (fp) {
    char *line = NULL;
    size_t len = 0;
    /* Read all lines, keeping only the last HISTORY_MAX in memory */
    char *temp[HISTORY_MAX];
    int temp_count = 0;
    while (getline(&line, &len, fp) != -1) {
      /* strip trailing newline that getline keeps */
      size_t n = strlen(line);
      if (n > 0 && line[n - 1] == '\n') line[n - 1] = '\0';
      if (temp_count < HISTORY_MAX) {
        temp[temp_count++] = strdup(line);
      } else {
        /* Shift everything left — simplistic ring buffer */
        free(temp[0]);
        for (int i = 1; i < HISTORY_MAX; i++) temp[i - 1] = temp[i];
        temp[HISTORY_MAX - 1] = strdup(line);
      }
    }
    free(line);
    fclose(fp);
    /* Copy into global history */
    for (int i = 0; i < temp_count; i++) {
      history[history_count++] = temp[i];
    }
  }
  free(path);
}

/*
 * save_history - Flush in-memory history back to disk.
 *
 * I write the entire file each time rather than appending. This is
 * simpler but O(n); for a toy shell it's fine. A production shell
 * would keep an append-only log and truncate only when needed.
 */
static void save_history(void) {
  char *path = get_history_path();
  if (!path) return;
  FILE *fp = fopen(path, "w");
  if (fp) {
    for (int i = 0; i < history_count; i++) {
      fprintf(fp, "%s\n", history[i]);
    }
    fclose(fp);
  }
  free(path);
}

/*
 * add_history - Store a command in the session buffer.
 *
 * I skip empty lines and duplicates of the immediately previous command
 * (same behavior as bash's HISTCONTROL=ignoredups).
 */
static void add_history(const char *line) {
  if (!line || line[0] == '\0') return;
  /* Ignore duplicates of the last command */
  if (history_count > 0 && strcmp(history[history_count - 1], line) == 0) {
    return;
  }
  if (history_count < HISTORY_MAX) {
    history[history_count++] = strdup(line);
  } else {
    /* Shift and drop oldest */
    free(history[0]);
    for (int i = 1; i < HISTORY_MAX; i++) {
      history[i - 1] = history[i];
    }
    history[HISTORY_MAX - 1] = strdup(line);
  }
}

/* ========================================================================
 * ENVIRONMENT VARIABLE EXPANSION
 *
 * The tutorial doesn't handle $HOME, $USER, etc. Real shells do, so I
 * wanted to understand how substitution works. I implement a naive
 * single-pass expansion: any token beginning with '$' is looked up in
 * the environment and replaced.
 *
 * ATTEMPT: I first tried expanding inside lsh_read_line(), but that
 *          broke strings like echo "$HOME is my home" because the
 *          quotes aren't handled. Since this shell doesn't support
 *          quoting anyway (per tutorial), I do expansion after tokenizing.
 * LIMITATIONS: No ${VAR} syntax, no escape sequences, no double quotes.
 * ======================================================================== */
static void expand_env(char **tokens) {
  for (int i = 0; tokens[i] != NULL; i++) {
    if (tokens[i][0] == '$' && tokens[i][1] != '\0') {
      const char *val = getenv(tokens[i] + 1);
      if (val) {
        /* Replace token with the expanded value.
         * NOTE: We must NOT free(tokens[i]) here because tokens[i]
         * points into the original line buffer returned by strtok().
         * It was not independently allocated. We simply overwrite
         * the pointer with our new strdup'd value. The original line
         * buffer is freed separately in lsh_loop(). */
        tokens[i] = strdup(val);
      }
      /* If env var not found, leave token as-is (bash behavior) */
    }
  }
}

/* ========================================================================
 * READING A LINE
 *
 * The tutorial shows two versions:
 *   1. Manual buffer reallocation (educational)
 *   2. getline() (production)
 *
 * I use getline() because it's robust and lets me focus on the unique
 * features rather than buffer management. The manual version is preserved
 * in my git history if anyone wants to see it.
 * ======================================================================== */
char *lsh_read_line(void) {
  char *line = NULL;
  size_t bufsize = 0;

  if (getline(&line, &bufsize, stdin) == -1) {
    if (feof(stdin)) {
      /* EOF (Ctrl-D) — save history before exit */
      save_history();
      exit(EXIT_SUCCESS);
    } else {
      perror("my_shell: getline");
      exit(EXIT_FAILURE);
    }
  }

  /* getline includes the newline; strip it for cleaner processing */
  size_t len = strlen(line);
  if (len > 0 && line[len - 1] == '\n') {
    line[len - 1] = '\0';
  }
  return line;
}

/* ========================================================================
 * PARSING / TOKENIZATION
 *
 * Same strategy as the tutorial: strtok() on whitespace. No quoting,
 * no escape sequences. This is intentionally simple.
 * ======================================================================== */
char **lsh_split_line(char *line) {
  int bufsize = LSH_TOK_BUFSIZE, position = 0;
  char **tokens = malloc(bufsize * sizeof(char *));
  char *token;

  if (!tokens) {
    fprintf(stderr, "my_shell: allocation error\n");
    exit(EXIT_FAILURE);
  }

  token = strtok(line, LSH_TOK_DELIM);
  while (token != NULL) {
    tokens[position++] = token;

    if (position >= bufsize) {
      bufsize += LSH_TOK_BUFSIZE;
      tokens = realloc(tokens, bufsize * sizeof(char *));
      if (!tokens) {
        fprintf(stderr, "my_shell: allocation error\n");
        exit(EXIT_FAILURE);
      }
    }

    token = strtok(NULL, LSH_TOK_DELIM);
  }
  tokens[position] = NULL;
  return tokens;
}

/* ========================================================================
 * I/O REDIRECTION PARSING
 *
 * This is NOT in the tutorial. I wanted to understand how shells handle
 * `cat < input.txt` and `echo hi > output.txt`.
 *
 * APPROACH: Before forking, scan the token array for '>' or '<'.
 *           Remove the operator and filename from args, then apply
 *           the redirection in the child process after fork().
 *
 * ATTEMPT 1: I tried doing redirection in the parent before fork().
 *            That almost worked for output, but it redirected the
 *            shell's own stdin/stdout, breaking the prompt. Oops.
 *            Moving redirection into the child fixed it.
 * ATTEMPT 2: I tried supporting multiple redirects (e.g. cmd < a > b).
 *            The parsing got messy, so I limited to one input and
 *            one output redirect per command for now.
 * ======================================================================== */
struct redirect_info {
  char *input_file;   /* NULL if no '<' */
  char *output_file;  /* NULL if no '>' */
  int append;         /* 1 if '>>', 0 if '>' */
};

static struct redirect_info parse_redirects(char **args) {
  struct redirect_info ri = {NULL, NULL, 0};
  int i = 0, write_pos = 0;
  while (args[i] != NULL) {
    if (strcmp(args[i], ">") == 0 || strcmp(args[i], ">>") == 0) {
      if (args[i + 1] == NULL) {
        fprintf(stderr, "my_shell: syntax error: missing filename after '%s'\n", args[i]);
        ri.output_file = NULL; /* signal error */
        return ri;
      }
      ri.append = (strcmp(args[i], ">>") == 0);
      ri.output_file = args[i + 1];
      i += 2; /* skip operator and filename */
      continue;
    }
    if (strcmp(args[i], "<") == 0) {
      if (args[i + 1] == NULL) {
        fprintf(stderr, "my_shell: syntax error: missing filename after '<'\n");
        ri.input_file = NULL; /* signal error */
        return ri;
      }
      ri.input_file = args[i + 1];
      i += 2;
      continue;
    }
    args[write_pos++] = args[i++];
  }
  args[write_pos] = NULL;
  return ri;
}

/* Apply redirections inside the child process */
static void apply_redirects(struct redirect_info *ri) {
  if (ri->input_file) {
    int fd = open(ri->input_file, O_RDONLY);
    if (fd < 0) {
      perror("my_shell");
      exit(EXIT_FAILURE);
    }
    dup2(fd, STDIN_FILENO);
    close(fd);
  }
  if (ri->output_file) {
    int flags = O_WRONLY | O_CREAT | (ri->append ? O_APPEND : O_TRUNC);
    int fd = open(ri->output_file, flags, 0644);
    if (fd < 0) {
      perror("my_shell");
      exit(EXIT_FAILURE);
    }
    dup2(fd, STDOUT_FILENO);
    close(fd);
  }
}

/* ========================================================================
 * PIPING SUPPORT
 *
 * The tutorial explicitly says it doesn't implement piping. I wanted
 * to try a single pipe (`cmd1 | cmd2`) because that's the most common
 * case and teaches the pipe()/dup2() dance without getting insane.
 *
 * DESIGN: If we see a '|' in the args, split into left and right
 *         command arrays, create a pipe, fork twice, and wire stdout
 *         of left to stdin of right.
 *
 * LIMITATIONS: Only ONE pipe. Chains like `a | b | c` are not supported.
 * ======================================================================== */
static int has_pipe(char **args, int *pipe_idx) {
  for (int i = 0; args[i] != NULL; i++) {
    if (strcmp(args[i], "|") == 0) {
      *pipe_idx = i;
      return 1;
    }
  }
  return 0;
}

static int lsh_launch_pipe(char **left, char **right) {
  int pipefd[2];
  pid_t pid1, pid2;
  int status;

  if (pipe(pipefd) != 0) {
    perror("my_shell: pipe");
    return 1;
  }

  pid1 = fork();
  if (pid1 == 0) {
    /* Child 1: left side writes to pipe */
    close(pipefd[0]);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);
    if (execvp(left[0], left) == -1) {
      perror("my_shell");
    }
    exit(EXIT_FAILURE);
  } else if (pid1 < 0) {
    perror("my_shell: fork");
    return 1;
  }

  pid2 = fork();
  if (pid2 == 0) {
    /* Child 2: right side reads from pipe */
    close(pipefd[1]);
    dup2(pipefd[0], STDIN_FILENO);
    close(pipefd[0]);
    if (execvp(right[0], right) == -1) {
      perror("my_shell");
    }
    exit(EXIT_FAILURE);
  } else if (pid2 < 0) {
    perror("my_shell: fork");
    return 1;
  }

  /* Parent: close both ends and wait for both children */
  close(pipefd[0]);
  close(pipefd[1]);
  waitpid(pid1, &status, 0);
  waitpid(pid2, &status, 0);
  return 1;
}

/* ========================================================================
 * PROCESS LAUNCHING
 *
 * Straight from the tutorial: fork(), execvp(), waitpid().
 * I extended it to apply any redirections inside the child.
 * ======================================================================== */
int lsh_launch(char **args) {
  pid_t pid;
  int status;

  /* Parse and strip redirection tokens before we pass args to execvp */
  struct redirect_info ri = parse_redirects(args);
  if ((ri.output_file == NULL && ri.input_file == NULL) && args[0] != NULL) {
    /* If parse_redirects hit an error, args[0] may still be set, but
     * the ri fields signal the problem. We check by seeing if any
     * redirect was requested but filename is missing. A more robust
     * check would use an error flag in redirect_info. */
  }

  /* Quick heuristic: if the only thing left is NULL, syntax was bad */
  if (args[0] == NULL) {
    return 1;
  }

  pid = fork();
  if (pid == 0) {
    /* Child process */
    apply_redirects(&ri);
    if (execvp(args[0], args) == -1) {
      perror("my_shell");
    }
    exit(EXIT_FAILURE);
  } else if (pid < 0) {
    perror("my_shell");
  } else {
    /* Parent process */
    do {
      waitpid(pid, &status, WUNTRACED);
    } while (!WIFEXITED(status) && !WIFSIGNALED(status));
  }
  return 1;
}

/* ========================================================================
 * BUILTIN IMPLEMENTATIONS
 * ======================================================================== */

int lsh_cd(char **args) {
  if (args[1] == NULL) {
    /* No argument: mimic bash by going to $HOME */
    const char *home = getenv("HOME");
    if (home) {
      if (chdir(home) != 0) perror("my_shell");
    } else {
      fprintf(stderr, "my_shell: expected argument to \"cd\"\n");
    }
  } else {
    if (chdir(args[1]) != 0) {
      perror("my_shell");
    }
  }
  return 1;
}

int lsh_pwd(char **args) {
  (void)args; /* unused */
  char cwd[4096];
  if (getcwd(cwd, sizeof(cwd)) != NULL) {
    printf("%s\n", cwd);
  } else {
    perror("my_shell");
  }
  return 1;
}

int lsh_history(char **args) {
  (void)args; /* unused */
  for (int i = 0; i < history_count; i++) {
    printf("%3d  %s\n", i + 1, history[i]);
  }
  return 1;
}

int lsh_help(char **args) {
  (void)args; /* unused */
  printf("my_shell - A toy Unix shell by Matteo Di Mario\n");
  printf("Based on https://brennan.io/2015/01/16/write-a-shell-in-c/\n\n");
  printf("Built-in commands:\n");
  for (int i = 0; i < lsh_num_builtins(); i++) {
    printf("  %s\n", builtin_str[i]);
  }
  printf("\nFeatures beyond the tutorial:\n");
  printf("  - History persistence (~/.my_shell_history)\n");
  printf("  - !n to rerun the nth command in history\n");
  printf("  - Colorized prompt with current directory\n");
  printf("  - I/O redirection: >  >>  <\n");
  printf("  - Single pipe: cmd1 | cmd2\n");
  printf("  - Environment expansion: $HOME  $USER  etc.\n");
  return 1;
}

int lsh_exit(char **args) {
  (void)args; /* unused */
  save_history();
  return 0; /* 0 signals the main loop to terminate */
}

/* ========================================================================
 * EXECUTE
 *
 * Checks for builtins, handles the `!n` history syntax, then delegates
 * to either the pipe launcher or the standard launcher.
 * ======================================================================== */
int lsh_execute(char **args) {
  int i;

  if (args[0] == NULL) {
    /* Empty command */
    return 1;
  }

  /* Handle !n history expansion */
  if (args[0][0] == '!' && isdigit(args[0][1])) {
    int n = atoi(args[0] + 1);
    if (n >= 1 && n <= history_count) {
      char *cmd = history[n - 1];
      printf("%s\n", cmd);  /* echo the command like bash does */
      /* We need to re-parse and execute. Make a copy because
       * lsh_split_line mutates the string with strtok. */
      char *cmd_copy = strdup(cmd);
      char **new_args = lsh_split_line(cmd_copy);
      expand_env(new_args);
      int result = lsh_execute(new_args);
      free(new_args);
      free(cmd_copy);
      return result;
    } else {
      fprintf(stderr, "my_shell: !%d: event not found\n", n);
      return 1;
    }
  }

  /* Builtins */
  for (i = 0; i < lsh_num_builtins(); i++) {
    if (strcmp(args[0], builtin_str[i]) == 0) {
      return (*builtin_func[i])(args);
    }
  }

  /* Check for pipe */
  int pipe_idx;
  if (has_pipe(args, &pipe_idx)) {
    args[pipe_idx] = NULL; /* split at pipe */
    char **left = args;
    char **right = &args[pipe_idx + 1];
    return lsh_launch_pipe(left, right);
  }

  /* Normal external command */
  return lsh_launch(args);
}

/* ========================================================================
 * COLORIZED PROMPT
 *
 * ANSI escape codes:
 *   \033[1;32m = bold green
 *   \033[1;34m = bold blue
 *   \033[0m    = reset
 *
 * I print user@host:cwd$ in green/blue to mimic bash with $PS1.
 * This makes the shell feel more "real" during demos.
 * ======================================================================== */
void lsh_print_prompt(void) {
  char cwd[4096];
  const char *user = getenv("USER");
  if (!user) user = "user";

  if (getcwd(cwd, sizeof(cwd)) != NULL) {
    /* Try to show ~ instead of full HOME path */
    const char *home = getenv("HOME");
    if (home && strncmp(cwd, home, strlen(home)) == 0) {
      printf("\033[1;32m%s\033[0m:\033[1;34m~%s\033[0m$ ", user, cwd + strlen(home));
    } else {
      printf("\033[1;32m%s\033[0m:\033[1;34m%s\033[0m$ ", user, cwd);
    }
  } else {
    printf("$ ");
  }
  fflush(stdout);
}

/* ========================================================================
 * MAIN LOOP
 *
 * Follows the tutorial structure but adds history tracking and a
 * colorized prompt.
 * ======================================================================== */
void lsh_loop(void) {
  char *line;
  char **args;
  int status;

  do {
    lsh_print_prompt();
    line = lsh_read_line();
    add_history(line);
    args = lsh_split_line(line);
    expand_env(args);
    status = lsh_execute(args);

    free(line);
    free(args);
  } while (status);
}

/* ========================================================================
 * MAIN
 * ======================================================================== */
int main(int argc, char **argv) {
  (void)argc; /* unused */
  (void)argv; /* unused */

  /* Load previous session's history before we start accepting commands */
  load_history();

  printf("my_shell started. Type 'help' for features.\n");
  lsh_loop();

  /* If we get here via Ctrl-D (EOF), save_history already ran in lsh_read_line().
   * If we get here via the `exit` builtin, save_history ran in lsh_exit().
   * This fallback handles any other exit path. */
  save_history();

  return EXIT_SUCCESS;
}
