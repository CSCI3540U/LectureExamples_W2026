#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define FLAG_FILE "flags/level04_layered.flag"
#define SHIFT 9

static const char *stored = "c3plcmlw";

/* Return the index of c in the base64 alphabet, or -1 if not found. */
static int b64_val(char c) {
    const char *alpha =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    const char *p = strchr(alpha, c);
    return p ? (int)(p - alpha) : -1;
}

/* Decode a base64 string. Returns a heap-allocated, null-terminated string. */
char *base64_decode(const char *src) {
    size_t len = strlen(src);
    char *out = malloc(len / 4 * 3 + 1);
    size_t o = 0;

    for (size_t i = 0; i + 3 < len; i += 4) {
        int b0 = b64_val(src[i]);
        int b1 = b64_val(src[i + 1]);
        int b2 = src[i + 2] == '=' ? 0 : b64_val(src[i + 2]);
        int b3 = src[i + 3] == '=' ? 0 : b64_val(src[i + 3]);

        out[o++] = (b0 << 2) | (b1 >> 4);
        if (src[i + 2] != '=') out[o++] = ((b1 & 0xf) << 4) | (b2 >> 2);
        if (src[i + 3] != '=') out[o++] = ((b2 & 0x3) << 6) | b3;
    }
    out[o] = '\0';
    return out;
}

/* Rotate lowercase letters forward by shift positions; leave others unchanged. */
void caesar(char *str, int shift) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] >= 'a' && str[i] <= 'z') {
            str[i] = 'a' + (str[i] - 'a' + shift) % 26;
        }
    }
}

/* Return 1 if str has exactly expected characters, 0 otherwise. */
int check_length(const char *str, size_t expected) {
    return strlen(str) == expected;
}

int main(void) {
    char *password = base64_decode(stored);
    caesar(password, SHIFT);

    char input[64];
    printf("Enter the password: ");
    if (fgets(input, sizeof(input), stdin) == NULL) {
        fprintf(stderr, "Read error.\n");
        free(password);
        return 1;
    }
    input[strcspn(input, "\n")] = '\0';

    if (!check_length(input, strlen(password))) {
        printf("Wrong password.\n");
        free(password);
        return 0;
    }

    if (strcmp(input, password) == 0) {
        FILE *f = fopen(FLAG_FILE, "r");
        if (f == NULL) {
            fprintf(stderr, "Flag file not found.\n");
            free(password);
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

    free(password);
    return 0;
}
