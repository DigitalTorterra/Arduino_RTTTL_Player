//beginning of generated code
#define NUM_SONGS 4

char *song_names[] = {"aadams","MissionImpossi","FightSong","Beethoven"};

const int aadams_frequency[] = {523,698,880,698,523,493,783,698,659,783,659,329,440,698,523,698,880,698,523,493,783,698,659,523,587,659,698,523,587,659,698,0,587,659,739,783,0,587,659,739,783,0,587,659,739,783,0,523,587,659,698};
const int aadams_duration[] = {187,375,187,375,187,375,750,187,375,187,375,187,375,750,187,375,187,375,187,375,750,187,375,187,375,187,1500,187,187,187,187,1500,187,187,187,187,1500,187,187,187,187,375,187,187,187,187,375,187,187,187,187};
const int MissionImpossi_frequency[] = {622,523,392,622,523,369,622,523,349,311,349,0,415,392,739,415,392,698,415,392,659,622,587,0};
const int MissionImpossi_duration[] = {166,166,1333,166,166,1333,166,166,1333,166,166,1333,166,166,1333,166,166,1333,166,166,1333,166,166,666};
const int FightSong_frequency[] = {392,369,392,415,415,392,415,0,415,415,415,392,415,466,466,415,466,523,622,587,523,466,392,311,392,349,329,392,349,329,349,466,0,392,392,392,369,392,415,392,415,0,415,415,415,392,415,466,466,415,466,523,622,587,523,466,392,311,349,392,466,415,392,349,311};
const int FightSong_duration[] = {857,428,428,214,428,214,214,642,214,428,214,428,428,214,428,214,857,428,428,428,428,428,428,857,214,428,214,428,428,214,428,428,642,214,428,214,428,428,642,214,214,642,214,428,214,428,428,214,428,214,857,428,428,428,428,428,428,428,428,214,428,214,428,428,1714};
const int Beethoven_frequency[] = {523,659,523,783,523,1046,987,880,783,880,783,698,659,698,659,587,523,659,783,659,1046,783};
const int Beethoven_duration[] = {375,375,375,375,375,375,187,187,187,187,187,187,187,187,187,187,375,375,375,375,375,375};

//This part will always contain the same arrays
const int *frequencies[] = {aadams_frequency,MissionImpossi_frequency,FightSong_frequency,Beethoven_frequency};
const int *durations[] = {aadams_duration,MissionImpossi_duration,FightSong_duration,Beethoven_duration};
const int song_lengths[] = {51,24,65,22};
//end of generated code

//function to translate from a track and address to the array
int * getNotes(int track, int addr) {
	static int data[2]; //initialize array

	//correct any possible overflow
	track %= NUM_SONGS;
	addr %= song_lengths[track];
	
	//grab the right values
	int frequency = *(frequencies[track]+addr);
	int duration = *(durations[track]+addr);
	
	//store the values in the output array
	data[0] = frequency;
	data[1] = duration;
	
	return data;
}


//Library Inclusion
#include <LiquidCrystal.h>
#include <toneAC.h> //needs pins 9 and 10

LiquidCrystal lcd(11,12,4,5,6,7); //setup the LCD display

volatile int track = 0; //the track number
volatile int addr = 0;  //the correct address
volatile int pause = 1; //whether or not to play music


void setup() {
	pinMode(2,INPUT); //interrupt input for skip
 	pinMode(3,INPUT); //interrupt input for pause/play
	
	attachInterrupt(0,skip,RISING); 
	attachInterrupt(1,play,RISING);
	
	lcd.begin(16,2); //initializing the LCD
 
  //Clearing the LCD and then displaying the first song
  lcd.setCursor(0,0);
  lcd.print("                ");
  lcd.setCursor(0,0);
  lcd.print(song_names[track % NUM_SONGS]);
}

void loop() {
  //only proceeds if pause is equal to 1	
	if (pause == 1) {
		//read volume from the potentiometer
		int volume = analogRead(A0);
		volume = map(volume,0,1023,0,10);
		
		//read in the correct frequency/duration from memory
		int *p;
		p = getNotes(track,addr);
		int frequency = *p;
		int duration = *(p+1);
		
		//play the correct tone, at the correct volume, for the right duration, and pause until done
		toneAC(frequency,volume,duration,false); 

		//increment addr
		addr++;
	}
}

void skip(){
	//the function to increment the track number
	track++;
	addr = 0;

  //also displays the new song text on the Arduino after clearing out the old
  lcd.setCursor(0,0);
  lcd.print("                ");
  lcd.setCursor(0,0);
  lcd.print(song_names[track % NUM_SONGS]);
}

void play(){
	//the function to pause/play the song
	pause *= -1;
}

