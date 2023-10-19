#include <ArduinoJson.h>

#define JSON_STR_LEN 400

// succeeds in getting json out of strings with junk on front and end of string

void addElementToJSON(char * jsonstr, char * key, float value) {
  int len = strlen(jsonstr);
  jsonstr[len - 1] = '\0'; // assuming this ends with '}'
  char buffer[40];

  sprintf(buffer, ",\"%s\":%.6f}", key, value);  
  strcat(jsonstr, buffer);
}

int findLast(char *str, char chr) {
  int index = -1;
  int len = strlen(str);
  for (int i = len - 1; i >=0; i--) {
    if (str[i] == chr) {
      index = i;
      return(index);
    }
  }
  return(-1);
}

char * trimJSONString(char *str) {
  char tmp[JSON_STR_LEN];

  char *ptr = strchr( str, '{' );

  strcpy(tmp, str);
  if (ptr != NULL) {
    strcpy(tmp, ptr);
  }

  int index = findLast( tmp, '}' );
  if (index != -1) {
    tmp[index + 1] = '\0';
  }

  strcpy(str, tmp);
  return(str);
}

void setup() {
  // Initialize serial port
  Serial.begin(9600);
  while (!Serial) continue;

  StaticJsonDocument<JSON_STR_LEN> doc;

  char json[JSON_STR_LEN];
  char temp[JSON_STR_LEN];

  strcpy(json, "[34muart[0m@MESC>{\"adc1\":689,\"ehz\":-0.171,\"error\":0,\"id\":0.152,\"iq\":-0.073,\"iqreq\":0.000,\"TMOS\":0.000,\"TMOT\":0.000,\"vbus\":56.997,\"Vd\":2.196,\"Vq\":0.676}[32assdfd332\0");
  
  trimJSONString(json);

  // that's fixed. now concatenated new values
  addElementToJSON(json, "angle", 0.90);
  strcpy(temp, json);
  DeserializationError error = deserializeJson(doc, temp);

  // Test if parsing succeeds.
  if (error) {
    Serial.print(F("deserializeJson() #2 failed: "));
    Serial.println(error.f_str());
  }
  else {
    Serial.println("#1 it worked");
  }

  Serial.print("fix5: ");
  Serial.println(json);
}

void loop() {
}
