#include <unistd.h>
#include <stdlib.h>

int main() {
    setuid(0);
    setgid(0);
    // VULNERABILITY: Relative path call to 'gzip'
    system("gzip -f /var/log/syslog.bak"); 
    return 0;
}
