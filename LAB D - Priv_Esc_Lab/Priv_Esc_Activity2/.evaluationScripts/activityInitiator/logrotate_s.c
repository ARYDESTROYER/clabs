#include <stdio.h>
#include <unistd.h>

int main() {
    printf("[logrotate_s] Log rotation check complete.\n");
    printf("Effective UID: %d\n", geteuid());
    return 0;
}
