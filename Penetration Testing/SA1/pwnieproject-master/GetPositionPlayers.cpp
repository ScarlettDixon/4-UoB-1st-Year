#include <dlfcn.h>
#include <set>
#include <map>
#include <iostream>
#include <fstream>
#include <vector>
#include <functional>
#include "libGameLogic.h" 
#include <chrono>
#include <cstring>
#include <thread>

// g++ GetPositionPlayers.cpp -shared -fPIC -o GetPositionPlayers.so
// LD_PRELOAD=GetPositionPlayers.so ./PwnAdventure3-Linux-Shipping 

std::ofstream myfile;

bool Player::CanJump() {
  return 1;
}


/* Gets all the players in a world that are within a specified radius */
int counter = 0; // Keeps track of number of calls for World::Tick()
float radius = 2000; 
int modulus = 25; // Sets how often the location extraction code is executed (e.g. every 25th call of Tick()) 
void World::Tick(float p){
    if (counter % modulus == 0) {
        myfile.open ("otherplayers.csv", std::ios::trunc);
        ClientWorld* world = *((ClientWorld**)(dlsym(RTLD_NEXT, "GameWorld")));
        
        /* Get the position of the active player */
        IPlayer* a_iplayer = world->m_activePlayer.m_object;
        IActor* a_iactor = a_iplayer->GetActorInterface();
        Actor* a_actor = (Actor *) a_iactor;
        Vector3 a_position = a_actor->GetPosition();
        
        /* Iterate over all the players in the specified radius and get their position */
        for(IPlayer* iplayer : world->GetPlayersInRadius(a_position, radius)) {
            IActor* iactor = iplayer->GetActorInterface();
            Actor* actor = (Actor *) iactor;
            /* Skip the active player */
            if ((actor->m_id) == (a_actor->m_id)) {
                continue;
            }
            Vector3 pos = actor->GetPosition();
            Player* player = (Player *) iplayer;
            printf("%s %f %f %f\n",player->m_playerName, (float)pos.x, (float)pos.y, (float)pos.z); 
            /* Write to CSV file: playerName, x, y, z */
            myfile << player->m_playerName << "," << (float) pos.x << "," << (float) pos.y << "," << (float) pos.z << "\n";          
        }
        myfile.close();
        counter = 0; // reset the counter
    }
    counter++;
}
