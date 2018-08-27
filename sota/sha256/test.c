#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <cassert>

#include "sha256.h"

extern char * sha256(const char *input);

int main(int argc, char *argv[]) {
    const char input[] = "sota is State Of The Art";
    const char expected[] = "82eec458d428bf742ec23b94396660e1c6a2e0495303469fe743d792666df56c";
    const char *output = sha256(input);
    assert(strcmp(output, expected) == 0);

    printf("sha256 of '%s' =>\n%s\n", input, output);
    free((char *)output);
    printf("buh-bye\n");
    return 0;
}
