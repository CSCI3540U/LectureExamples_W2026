#include <stdio.h>
#include <string.h>

#define FLAG_FILE "flags/level01_strings.flag"
#define PASSWORD  "opensesame"

int main(void) {
    char input[64];

    printf("Enter the password: ");
    if (fgets(input, sizeof(input), stdin) == NULL) {
        fprintf(stderr, "Read error.\n");
        return 1;
    }

    /* Strip trailing newline */
    input[strcspn(input, "\n")] = '\0';

    if (strcmp(input, PASSWORD) == 0) {
        FILE *f = fopen(FLAG_FILE, "r");
        if (f == NULL) {
            fprintf(stderr, "Flag file not found.\n");
            return 1;
        }
        char flag[128];
        if (fgets(flag, sizeof(flag), f) != NULL) {
            printf("Correct! Flag: %s", flag);
        }
        fclose(f);
    } else {
        printf("Wrong password.\n");
    }

    return 0;
}
