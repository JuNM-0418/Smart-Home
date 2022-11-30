// C++ code
//
/*
  Sweep

  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 8 Nov 2013  by Scott Fitzgerald
  http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

int door_pos = 0;
int valve_pos = 0;
int window_pos = 0;

bool door_state = 0;
bool valve_state = 0;
bool window_state = 0;

int gas;
int pir_value;
  
Servo servo_9;
Servo servo_8;
Servo servo_7;


void OpenDoor(int& door_pos, bool& door_state) {
  for (door_pos = 0; door_pos <= 180; door_pos += 1) {
    servo_9.write(door_pos);
    delay(15); 
  }
  door_state = 1;
}

void CloseDoor(int& door_pos, bool& door_state) {
  for (door_pos = 180; door_pos >= 0; door_pos -= 1) {
    servo_9.write(door_pos); 
    delay(15); 
  }
  door_state = 0;
}

void OpenGasValve(int& valve_pos, bool& valve_state){
  for(valve_pos = 0; valve_pos <=90; valve_pos+= 1) {
  	servo_8.write(valve_pos);
    delay(15);
  }
  valve_state = 1;
}

void CloseGasValve(int& valve_pos, bool& valve_state){
  for(valve_pos = 90; valve_pos >=0; valve_pos-= 1) {
  	servo_8.write(valve_pos);
    delay(15);
  }
  valve_state = 0;
}

void OpenWindow(int& window_pos, bool& window_state) {
  for(window_pos = 0; window_pos <=180; window_pos+= 1) {
  	servo_8.write(window_pos);
    delay(15);
  }
  window_state = 1;
}

void CloseWindow(int& window_pos, bool& window_state) {
  for(window_pos = 180; window_pos >=0; window_pos-= 1) {
  	servo_8.write(window_pos);
    delay(15);
  }
  window_state = 1;
}

void setup()
{
  Serial.begin(9600);
  servo_9.attach(9, 500, 2500);
  servo_8.attach(8, 500, 2500);
  servo_7.attach(7, 500, 2500);
  pinMode(6, OUTPUT);
  pinMode(5, INPUT);

}

void loop()
{
  /**
  if(door_state == 0) {
  	OpenDoor(door_pos, door_state); 
    Serial.println("Door Open");
  }
  
  if (valve_state == 0) {
    OpenGasValve(valve_pos, valve_state);
    Serial.println("Valve Open");
  }
  
  if (door_state == 1) {
    CloseDoor(door_pos, door_state);
    Serial.println("Door Close");
  }
  
  
  if (valve_state == 1) {
  	CloseGasValve(valve_pos, valve_state);  
    Serial.println("Valve Close");
  }
  gas = analogRead(A2);
  Serial.println(gas);
  delay(1000);
  
  **/
  pir_value = digitalRead(5);
  Serial.println(pir_value);
  if(pir_value == HIGH) {
  	digitalWrite(6, HIGH);
  }
  else {
  	digitalWrite(6, LOW);
  }
  
 

}