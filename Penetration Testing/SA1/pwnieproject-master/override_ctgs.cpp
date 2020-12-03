#include <dlfcn.h>
#include <set>
#include <map>
#include <functional>
#include <string>
#include <cstring>
#include <vector>
#include <cstdio>
#include <stdint.h>
#include "libGameLogic.h"

//void GameAPI::ConnectToGameServer(const char *a, uint16_t b, int32_t c, const char * d) 

void GameAPI::ConnectToGameServer(const char *url, uint16_t port, int32_t idk, const char * hash)  
{
    // Recover the origonal method. Use the mangled method name here
    void *tmpPtr = dlsym(RTLD_NEXT, "_ZN7GameAPI19ConnectToGameServerEPKctiS1_");

    // Regular casting doesn't work, so we manually memcpy into something of the correct type
    typedef void (GameAPI::*methodType)(const char *url, uint16_t port, int32_t idk, const char * hash) const;
	static methodType origFunc = 0;
    memcpy(&origFunc, &tmpPtr, sizeof(&tmpPtr));

    printf("[Override] Redirecting connection to proxy on localhost. Port is %d\n", port);

    // Call the original method
    (this->*origFunc)("127.0.0.1", port, idk, hash);
}
