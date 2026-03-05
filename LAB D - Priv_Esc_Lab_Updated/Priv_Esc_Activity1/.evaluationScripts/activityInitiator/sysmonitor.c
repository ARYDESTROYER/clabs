#include <stdio.h>
#include <unistd.h>

int main() {
    printf("[sysmonitor] System status check complete.\n");
    printf("Effective UID: %d\n", geteuid());
    return 0;
}
