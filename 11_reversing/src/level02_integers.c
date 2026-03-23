#include <stdio.h>
#include <string.h>

#define FLAG_FILE "flags/level02_integers.flag"

int main(void) {
    int secret = 7331;
    char password[32];
    char input[64];

    /* Derive the password from the secret at runtime */
    snprintf(password, sizeof(password), "%d", secret * 3);

    printf("Enter the password: ");
    if (fgets(input, sizeof(input), stdin) == NULL) {
        fprintf(stderr, "Read error.\n");
        return 1;
    }
    input[strcspn(input, "\n")] = '\0';

    if (strcmp(input, password) == 0) {
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
