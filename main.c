#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

#include <net/if.h>
#include <linux/if_tun.h>
#include <linux/if_ether.h>

int main(int argc, const char **argv) {

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
	// Set interface name
    strncpy(ifr.ifr_name, "tunnel0", IFNAMSIZ);
    ifr.ifr_flags = IFF_TAP;
    FILE *f = fopen("test", "wb");
    fwrite(&ifr, sizeof(ifr), 1, f);
    fclose(f);

    int fd = open("/dev/net/tun", O_RDWR);
    if (fd < 0)
    {
        perror("open");
        return -1;
    }
    printf("%ld\n", TUNSETIFF);
    if (ioctl(fd, TUNSETIFF, (void *) &ifr) < 0)
    {
        fprintf(stderr, "Unable to configure tuntap device: ");
        perror("ioctl");
        return -1;
    }

    return 0;
}