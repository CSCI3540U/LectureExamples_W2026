#include <stdio.h>
#include <string.h>

#define FLAG_FILE "flags/level03_caesar.flag"

/* Rotate lowercase letters by shift positions; leave all other characters unchanged. */
void caesar(char *str, int shift) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] >= 'a' && str[i] <= 'z') {
            str[i] = 'a' + (str[i] - 'a' + shift) % 26;
        }
    }
}

int main(void) {
    const char *encoded = "jyhjrtl";
    int shift = 7;
    char input[64];

    printf("Enter the password: ");
    if (fgets(input, sizeof(input), stdin) == NULL) {
        fprintf(stderr, "Read error.\n");
        return 1;
    }
    input[strcspn(input, "\n")] = '\0';

    caesar(input, shift);

    if (strcmp(input, encoded) == 0) {
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
