// 코드 시작

#include <Servo.h>
#include <SimpleDHT.h>
#include <ArduinoJson.h>
// #include <SoftwareSerial.h>

class Button {
private:
  bool state = false;  // 현재 값
  bool prev = false;
  int pin;  // 핀 번호
public:
  Button(int pin) {
    this->pin = pin;
    pinMode(pin, INPUT_PULLUP);
  }
  void setPin(int pin) {
    this->pin = pin;
  }
  void change() {
    bool sensor = !digitalRead(this->pin);
    if (sensor && this->prev != sensor) {
      this->state = !this->state;
    }
    this->prev = sensor;
  }
  bool getState() {
    return this->state;
  }
  bool setState(bool s) {
    this->state = s;
  }
  void off() {
    this->state = false;
  }
  void on() {
    this->state = true;
  }
};  // 버튼 선언
/*
class SystemButton : public Button {
  private:
    Button btns[MAXBTN];
    int btnCount = 0;
  public:
    void add(Button& btn) {
      if (btnCount == MAXBTN) return;
      btns[btnCount++] = btn;
    }
    void off() {
      Button::off();
      for (Button b : btns) b.off();
    }

    void on() {
      Button::on();
      for (Button b : btns) b.on();
    }
};
*/
// 서보 선언 부
class SvHandler : public Servo {
private:
  int openVal, closeVal;

public:
  int svState = false;
  SvHandler(int op, int cl) {
    this->openVal = op;
    this->closeVal = cl;
  }

  void open() {
    svState = true;
    this->write(this->openVal);
  }
  void close() {
    svState = false;
    this->write(this->closeVal);
  }
};

SvHandler window1(90, 0);
SvHandler window2(90, 0);
SvHandler gasValve(0, 90);

Button mainLightButton(2);  // 핀번호 1에 할당
Button subLightButton(3);
Button toiletLightButton(4);
Button systemButton(5);

// 레지스터 제어 변수
int regi_data = 11;
int regi_latch = 10;
int regi_shift = 9;

SimpleDHT11 dht11(12);  // 핀번호 0에 할당
byte temperature = 0;
byte humidity = 0;

byte ledState = 0B00000000;

byte regi_OnAirc = B00000010;   //2
byte regi_OnHeat = B00000100;   //3
byte regi_OnHumi = B00001000;   //4
byte regi_OnDehum = B00010000;  //5
byte regi_OnMainL = B00100000;  //6
byte regi_OnSubL = B01000000;   //7
byte regi_OnToL = B10000000;    //8

byte regi_OffAirc = B11111101;
byte regi_OffHeat = B11111011;
byte regi_OffHumi = B11110111;
byte regi_OffDehum = B11101111;
byte regi_OffMainL = B11011111;
byte regi_OffSubL = B10111111;
byte regi_OffToL = B01111111;

// const size_t bufferSize = 2 * JSON_ARRAY_SIZE(3) + JSON_OBJECT_SIZE(2) + 6 * JSON_OBJECT_SIZE(3) + 240;
// DynamicJsonBuffer jsonBuffer(bufferSize);

DynamicJsonDocument in(50);
DynamicJsonDocument out(50);

int gasValue = 0;

unsigned long past = 0;

// Button& decision(String str) {

//   if (str.equals("거실")) {
//     return btn[0];
//   } else if (str.equals("침실")) {
//     return btn[1];
//   } else if (str.equals("화장실")) {
//     return btn[2];
//   }
// }

void setup() {
  Serial.begin(9600);
  //Serial.begin(9600);
  window1.attach(6);  // 5번 포트
  window2.attach(7);
  gasValve.attach(8);
  Serial.println("software begin");

  pinMode(regi_data, OUTPUT);
  pinMode(regi_latch, OUTPUT);
  pinMode(regi_shift, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  // 온습도 JSON 송신
  unsigned long now = millis();
  if (now - past >= 2000) {
    String des;
    dht11.read(&temperature, &humidity, NULL);  // 지속적으로 온도, 습도 인식
    // Serial.println((int)temperature);
    // Serial.println((int)humidity);
    out["temp"] = (int)temperature;
    out["humidity"] = (int)humidity;
    serializeJson(out, des);
    Serial.println(des);
    past = now;
  }
  // 제어 JSON 수신
  // ---------------------------------
  if (Serial.available()) {
    String jsonString = "";
    jsonString = Serial.readStringUntil('\n');
    // Serial.println(jsonString);
    deserializeJson(in, jsonString);
    String type = in["type"].as<String>();
    bool controlState = in["state"].as<String>().equals("on");
    Serial.println(jsonString);
    if (type.equals("거실")) {
      mainLightButton.setState(controlState);
    }
    if (type.equals("화장실")){
      subLightButton.setState(controlState);
    }
    if(type.equals("침실")){
      toiletLightButton.setState(controlState);
    }
    if(type.equals("전체")){
      systemButton.setState(controlState);
    }
    if(type.equals("창문")){
      if(controlState){
        window1.open();
        window2.open();
      }
      else{
        window1.close();
        window2.close();
      }
    }
    if(type.equals("가스 밸브")){
      if(controlState){
        gasValve.open();
      }else{
        gasValve.close();
      }
    }
    if(type.equals("가습기")){
      if(controlState){
    ledState = ledState | regi_OnHumi;
    }
    else{
    ledState = ledState & regi_OffHumi;
      }
    }
    if(type.equals("제습기")){
            if(controlState){
    ledState = ledState | regi_OnDehum;
    }
    else{
    ledState = ledState & regi_OffDehum;    
      }
    }
    if(type.equals("에어컨")){
      if(controlState){
        ledState = ledState | regi_OnAirc;
        }
      else{
        ledState = ledState & regi_OffAirc;
      }
    }
    if(type.equals("히터")){
      if(controlState){
        ledState = ledState | regi_OnHeat;
      }
      else{
        ledState = ledState & regi_OffHeat;
      }
    }
  }

  // 온습도 제어 부
  if ((int)temperature > 40){
    ledState = ledState | regi_OnAirc;
  }
  else{
    ledState = ledState & regi_OffAirc;
  }
  if((int)temperature < 20){
    ledState = ledState | regi_OnHeat;
  }
  else{
    ledState = ledState & regi_OffHeat;
  }
  if((int)humidity > 80){
    ledState = ledState | regi_OnDehum;
  }
  else{
    ledState = ledState & regi_OffDehum;
  }
  if((int)humidity < 20){
    ledState = ledState | regi_OnHumi;
  }
  else{
    ledState = ledState & regi_OffHumi;
  }

  // 가스 탐지 부
  // ----------------------------------
  gasValue = analogRead(A0);
  //Serial.println(gasValue);
  if (gasValue >= 500 && gasValve.svState == true){
    gasValve.close();
  }

  // ----------------------------------

  //버튼 입력 부
  //-----------------------------

  mainLightButton.change();
  subLightButton.change();
  toiletLightButton.change();
  systemButton.change();

  /*
  Serial.print("main: ");
  Serial.println(mainLightButton.getState());
  Serial.print("sub: ");
  Serial.println(subLightButton.getState());
  Serial.print("to: ");
  Serial.println(toiletLightButton.getState());
  Serial.print("sys: ");
  Serial.println(systemButton.getState());
  */

  // 모든 제어.
  //------------------------------------
  
  if (mainLightButton.getState()) {
    ledState = ledState | regi_OnMainL;
  } else{
    ledState = ledState & regi_OffMainL;
  }
  if (subLightButton.getState()) {
    ledState = ledState | regi_OnSubL;
  } else {
    ledState = ledState & regi_OffSubL;
  }
  if (toiletLightButton.getState()) {
    ledState = ledState | regi_OnToL;
  } else {
    ledState = ledState & regi_OffToL;
  }
  if (systemButton.getState()) {

  } else {
    ledState = ledState & regi_OffMainL;
    ledState = ledState & regi_OffSubL;
    ledState = ledState & regi_OffToL;
  }
  //Serial.print("ledState: ");
  //Serial.println(ledState, BIN);

  // led 조작 부
  // ------------------------------
  digitalWrite(regi_latch, LOW);  
  shiftOut(regi_data, regi_shift, MSBFIRST, ledState);
  delay(100);
  digitalWrite(regi_latch, HIGH);

}
