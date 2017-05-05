#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "flight_map.h"

// A safe version of malloc, that will exit the program in case your allocation
// fails.
void *checked_malloc(size_t size) {
     void *ptr = malloc(size);
     if (ptr == NULL) {
          fprintf(stderr, "memory allocation failed\n");
          exit(1);
     }
     return ptr;
}

struct map_t {
     char* city_name;
     struct map_t* next;
     struct map_t* connected;
     // YOUR CODE HERE
};

map_t* map_create() {
     // YOUR CODE HERE
     map_t* city = NULL;
     city = malloc(sizeof(map_t));
     map_free(city);
     return city;
}

void map_free(map_t* map) {
     // YOUR CODE HERE
     free(map);
}

int add_city(map_t* map, const char* name) {
     // YOUR CODE HERE
     map_t* temp = map;
     while (temp->next != NULL) {
          if (strcmp(temp->city_name, name) == 0) {
               return 0;
          }
          temp = temp->next;
     }
     if(strcmp(temp->city_name, name) == 0) {
          return 0;
     }
     map_t* new_city = map_create();
     new_city->city_name = name;
     temp->next = malloc(sizeof(map_t));
     free(temp->next);
     temp->next = new_city;
     return 1;
}

int remove_city(map_t* map, const char* name) {
     // YOUR CODE HERE
     map_t* temp1 = map->next;
     map_t* temp2 = map;
     if (strcmp(map->city_name, name) == 0) {
          map = map->next;
     }
     while(temp1 != NULL) {
          if (strcmp(temp1->city_name, name) == 0) {
               temp2->next = temp1->next;
               free(temp);
               return 1;
          }
          temp2 = temp1;
          temp1 = temp1->next;
     }
     return 0;
}

int num_cities(map_t* map) {
     // YOUR CODE HERE
     int count = 0;
     map_t* temp = map;
     while(temp != NULL) {
          count++;
          temp = temp->next;
     }
}

int link_cities(map_t* map, const char* city1_name, const char* city2_name) {
     // YOUR CODE HERE
}

int unlink_cities(map_t* map, const char* city1_name, const char* city2_name) {
     // YOUR CODE HERE
}

const char** linked_cities(map_t* map, const char* city_name) {
     // YOUR CODE HERE
}

const char** find_path(map_t* map, const char* src_name, const char* dst_name) {
     // YOUR CODE HERE
}

void map_export(map_t* map, FILE* f) {
     // YOUR CODE HERE
}

map_t* map_import(FILE* f) {
     // YOUR CODE HERE
     return NULL;
}
