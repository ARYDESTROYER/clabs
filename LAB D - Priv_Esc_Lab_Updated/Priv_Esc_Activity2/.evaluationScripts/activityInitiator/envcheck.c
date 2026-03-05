#include <stdio.h>
#include <unistd.h>

int main() {
    printf("[envcheck] Environment check complete.\n");
    printf("Effective UID: %d\n", geteuid());
    return 0;
}
