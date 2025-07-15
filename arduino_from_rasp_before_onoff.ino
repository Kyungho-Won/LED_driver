const int outPin = 8;

void setup() {
  pinMode(outPin, OUTPUT);
  digitalWrite(outPin, LOW);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // 명령 형식: pulse_XXXms (예: pulse_1ms, pulse_1000ms)
    if (cmd.startsWith("pulse_") && cmd.endsWith("ms")) {
      // 숫자 부분만 추출
      cmd.remove(0, 6);              // "pulse_" 제거
      cmd.remove(cmd.length() - 2);  // "ms" 제거

      int duration_ms = cmd.toInt();
      if (duration_ms > 0) {
        unsigned long start = micros();
        unsigned long duration_us = duration_ms * 1000UL;

        digitalWrite(outPin, HIGH);
        while (micros() - start < duration_us);  // 정밀 지연
        digitalWrite(outPin, LOW);
      }
    }
  }
}
