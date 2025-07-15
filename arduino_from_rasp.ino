const int outPin = 8; // LED_BUILTIN 또는 원하는 핀 번호로 변경

unsigned long pulse_start_time = 0;
bool pulse_active = false;
unsigned long pulse_duration_us = 0;

void setup() {
  pinMode(outPin, OUTPUT);
  digitalWrite(outPin, LOW);
  Serial.begin(9600); // Raspberry pi와 USB 포트를 통해 연결됨 (Raspberry pi output: usb-A, Arduino input: usb-c)
  while (!Serial) {
    ; // 시리얼 연결 대기 (필요 시)
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

	// Raspberry pi GUI 상에서 누른버튼에 따라 pulse_ms로 전송 
	// GUI에서 ms 대신 s를 선택해도 ms로 변환되어서 문자열로 전송한 것을 parcing, ms 추출
    if (input.startsWith("pulse_")) {
      int durationStart = 6;
      int durationEnd = input.indexOf("ms");
      if (durationEnd > durationStart) {
        int duration_ms = input.substring(durationStart, durationEnd).toInt();
        pulse_duration_us = (unsigned long)duration_ms * 1000;
        pulse_start_time = micros(); // microsecond 단위로 딜레이 측정 
        digitalWrite(outPin, HIGH);
        pulse_active = true;
      }
    } else if (input == "on") {
      digitalWrite(outPin, HIGH);
      pulse_active = false; // 수동 제어 상태로 전환, off 버튼을 누르기 전까지 계속해서 켜져있는 상태
    } else if (input == "off") {
      digitalWrite(outPin, LOW);
      pulse_active = false;
    }
  }

  // 고정밀 타이머 제어 (ON 버튼을 누른상태에서는 pulse 입력을 받지않도록 설계)
  if (pulse_active && (micros() - pulse_start_time >= pulse_duration_us)) {
    digitalWrite(outPin, LOW);
    pulse_active = false;
  }
}
