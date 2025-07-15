const int outPin = 8; // LED_BUILTIN 또는 원하는 핀 번호로 변경

unsigned long pulse_start_time = 0;
bool pulse_active = false;
unsigned long pulse_duration_us = 0;

void setup() {
  pinMode(outPin, OUTPUT);
  digitalWrite(outPin, LOW);
  Serial.begin(9600);
  while (!Serial) {
    ; // 시리얼 연결 대기 (필요 시)
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("pulse_")) {
      int durationStart = 6;
      int durationEnd = input.indexOf("ms");
      if (durationEnd > durationStart) {
        int duration_ms = input.substring(durationStart, durationEnd).toInt();
        pulse_duration_us = (unsigned long)duration_ms * 1000;
        pulse_start_time = micros();
        digitalWrite(outPin, HIGH);
        pulse_active = true;
      }
    } else if (input == "on") {
      digitalWrite(outPin, HIGH);
      pulse_active = false; // 수동 제어 상태로 전환
    } else if (input == "off") {
      digitalWrite(outPin, LOW);
      pulse_active = false;
    }
  }

  // 고정밀 타이머 제어
  if (pulse_active && (micros() - pulse_start_time >= pulse_duration_us)) {
    digitalWrite(outPin, LOW);
    pulse_active = false;
  }
}
