#include <dlfcn.h>
#include <set>
#include <map>
#include <functional>
#include <string.h>
#include <cstring>
#include <vector>
#include <cstdio>
#include <stdint.h>
#include <string.h>
#include <iostream>
#include <fstream>
#include <string> 
#include "libGameLogic.h" //header for target program

//Compiling the code
    //g++ hook.cpp -shared -fPIC -o hook.so

//Running the code
    //LD_PRELOAD=flying.so ./PwnAdventure3-Linux-Shipping

bool teleport; //initialise variables
typedef void (*orig_pos)(Player *, const Vector3 *); //define types
typedef void (*orig_chat)(Player *, const char *);
typedef void (*orig_tick)(World *, float f);

bool Player::CanJump(){ //allows player to jump in the air - we can fly!
    return 1; //set to true
}

void Player::Chat(const char *msg){ //override the player chat function
    printf("[chat] msg=\"%s\"\n", msg); //display chat messages in terminal

    if(strncmp("tp ", msg, 3) == 0){ //checks if msg starts with the string tp
        teleport = true; //sets teleport to true
        Vector3 pos; //initialise pos as Vector{float, float, float}

        //LOCATIONS - CAN BE ADDED FOR SPECIFIC POSITIONS
        if(strncmp("pos", msg+3, 3) == 0){ //teleport to any position
            sscanf(msg+7, "%f %f %f", &(pos.x), &(pos.y), &(pos.z)); //scans the chat for float values and assigns to vector attributes
        } else if(strncmp("FortBlox", msg+3, 10) == 0){ //teleport to "Fort"
            pos.x = -18450.0; //sets x value of pos
            pos.y = -4360.0; //sets y value of pos
            pos.z = 2225.0; //sets z value of pos
        } else if(strncmp("Town", msg+3, 10) == 0){ //teleport to "Town"
            pos.x = -39130.0;
            pos.y = -20280.0;
            pos.z = 2530.0;
        } else if(strncmp("GreatBallsOfFire", msg+3, 16) == 0){
            pos.x = -43655.0; 
            pos.y = -55820.0;
            pos.z = 322.0;
        } else if(strncmp("LostCaveBush", msg+3, 12) == 0){
            pos.x = -53539.0; 
            pos.y = -44246.0;
            pos.z = 358.0;
        } else if (strncmp("BearChest", msg+3, 8) == 0){
            pos.x = -7894.0; 
            pos.y = -64482.0;
            pos.z = 2663.0;
        }  else if (strncmp("CowChest", msg+3, 8) == 0){
            pos.x = 252920.0; 
            pos.y = -243800.0;
            pos.z = 1170.0;
        } else if (strncmp("TailMountain", msg+3, 8) == 0){
            pos.x = .0; 
            pos.y = .0;
            pos.z = .0;
        } else if (strncmp("GoldenEgg1", msg+3, 11) == 0){ //teleport to GoldenEggs
            pos.x = -25032.0; 
            pos.y = 17962.0;
            pos.z = 266.0;
        } else if (strncmp("GoldenEgg2", msg+3, 11) == 0){
            pos.x = -51570.0; 
            pos.y = -61215.0;
            pos.z = 5020.0;
        } else if (strncmp("GoldenEgg3", msg+3, 11) == 0){
            pos.x = 24512.0; 
            pos.y = 69682.0;
            pos.z = 2659.0;
        } else if (strncmp("GoldenEgg4", msg+3, 11) == 0){
            pos.x = 60453.0; 
            pos.y = -17409.0;
            pos.z = 2939.0;
        } else if (strncmp("GoldenEgg5", msg+3, 11) == 0){
            pos.x = 1522.0; 
            pos.y = -14966.0;
            pos.z = 7022.0;
        } else {
            teleport = false; //initialise teleport to false
            
            orig_chat orig;
            orig = (orig_chat) dlsym(RTLD_NEXT, "_ZN6Player4ChatEPKc"); //call demangled function address
            orig(this, "[!CHAT]Wrong Location!"); //display in game chat //[!CHAT] - Proxy picks up flag and does not display messages to other players on game
        }   
        
        if(teleport){ //sets position if teleport = true
            const Vector3 p = pos;
            orig_pos orig;
            orig = (orig_pos) dlsym(RTLD_NEXT, "_ZN5Actor11SetPositionERK7Vector3"); //returns address of where function is loaded into memory
            orig(this, &p); //calls set player function on p
        }

    } else if(strncmp("jp", msg, 2) == 0){ //increase/decrease player jump speed
        if(strncmp("+", msg+2, 1) == 0){ //test if increase
            this->m_jumpSpeed = this->m_jumpSpeed * 2; //increase player jump speed by * 2
        } else if(strncmp("-", msg+2, 1) == 0){ //test if decrease
            this->m_jumpSpeed = this->m_jumpSpeed / 2; //decrease player jump speed by / 2
        }
    } else if(strncmp("sp", msg, 2) == 0){ //increase/decreease player walking speed
        if(strncmp("+", msg+2, 1) == 0){ 
            this->m_walkingSpeed = this->m_walkingSpeed * 2;
        } else if(strncmp("-", msg+2, 1) == 0){
            this->m_walkingSpeed = this->m_walkingSpeed / 2;
        }
    } else if(strncmp("getPos", msg, 6) == 0){ //gets current position of user
        Vector3 getpos = this->GetPosition(); //assigns getpos with the current position of the player
        
        printf("Current Position: x: %2f y: %2f z: %2f\n", getpos.x, getpos.y, getpos.z); //output position to terminal

        std::string locx = std::to_string(getpos.x); //convert float values to string
        std::string locy = std::to_string(getpos.y);
        std::string locz = std::to_string(getpos.z);
        std::string all_loc = "[!CHAT]My Location: x:" + locx + ", y:" + locy + ", z:" + locz; //display location to chat
        
        const char* curLoc = all_loc.c_str(); //convert string message to const char

        orig_chat orig;
        orig = (orig_chat) dlsym(RTLD_NEXT, "_ZN6Player4ChatEPKc"); //call player chat function
        orig(this, curLoc); //display location message
    } else { //call original chat function
        orig_chat orig;
        orig = (orig_chat) dlsym(RTLD_NEXT, "_ZN6Player4ChatEPKc");
        orig(this, msg);
    }
}

int counter = 0; //initialise variables
int modulus = 25;
bool firstRun = true;
std::string oldx, oldy, oldz;
std::string oldclick;

void World::Tick(float f){ //call world tick function
    
    // get active player
    ClientWorld* world = *((ClientWorld**)(dlsym(RTLD_NEXT, "GameWorld"))); //load pointer to game world object
    IPlayer* iplayer = world->m_activePlayer.m_object;
    Player* player = (Player*) iplayer;
    
    if (firstRun) {
        //std::cout << "[FIRST RUN]" << std::endl; //output to console

        std::ifstream myfile("Map/clickteleport.csv"); //open file
        std::getline(myfile, oldclick, ' '); //assign data from csv to variables
        std::getline(myfile, oldx, ' '); //each variable in file is seperated by a space
        std::getline(myfile, oldy, ' ');
        std::getline(myfile, oldz, '\n');

        //std::cout << "[old x] " << oldx << std::endl; //output to console
        //std::cout << "[old y] " << oldy << std::endl;   
        //std::cout << "[old z] " << oldz << std::endl;   

        firstRun = false; //set to false after first run
    }

    if (counter % modulus == 0) { //test against modulus - this function is run once every 25 ticks/times the function is called
        std::ifstream myfile("Map/clickteleport.csv"); //open file
        
        std::string click; //initialise variables
        std::string posx;
        std::string posy;
        std::string posz;
        
        std::getline(myfile, click, ' '); //read each element from file
        std::getline(myfile, posx, ' ');
        std::getline(myfile, posy, ' ');
        std::getline(myfile, posz, '\n');
        
        //std::cout << "[click]=" << click << std::endl; //output to console
        //std::cout << "[x] " << posx << std::endl;  
        //std::cout << "[y] " << posy << std::endl;
        //std::cout << "[z] " << posz << std::endl;
        
        if((oldx.compare(posx)) != 0 || (oldy.compare(posy)) != 0 ) { //test if old location values are the same so to not teleport randomly
        
            Vector3 teleportPosition = player->GetPosition(); // create position for teleportation

            teleportPosition.x = std::stof(posx); //converts data read from file (string) to float
            teleportPosition.y = std::stof(posy);
            teleportPosition.z = 15500; //player then falls down into position

            //std::cout << "[x teleport]" << teleportPosition.x; //output to terminal
            //std::cout << "[y teleport]" << teleportPosition.y;
            //std::cout << "[z teleport]" << teleportPosition.z;

            player->SetPosition(teleportPosition); // teleport player to new position

            oldx.assign(posx); //assign new values to old value
            oldy.assign(posy);

            std::string allpos = "[!CHAT]Teleported to: x:" + posx + ", y:" + posy + ", z:" + posz; //output to chat
                        
            const char* position = allpos.c_str(); //convert string to const char so msg can be displayed

            orig_chat orig;
            orig = (orig_chat) dlsym(RTLD_NEXT, "_ZN6Player4ChatEPKc"); //call player chat function
            orig(player, position); //display position of user in chat
        }    
        counter=0;
    }
    counter++;

    orig_tick orig;
    orig = (orig_tick) dlsym(RTLD_NEXT, "_ZN5World4TickEf"); //call original world tick function for normal use
    orig(world, f);
}