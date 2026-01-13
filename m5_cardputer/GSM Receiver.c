/*
 * GSM_Receiver.c
 *
 * Created: 7/5/2014 7:16:02 PM
 *  Author: Saroj Shakya
 */ 


#include <avr/io.h>
#define F_CPU 16000000UL
#include <util/delay.h>
#define LCD_DATAPORT PORTB
#define LCD_DATADDR DDRB
#define LCD_CMNDPORT PORTC
#define LCD_CMNDDDR DDRC
#define LCD_RS 0
#define LCD_RW 1
#define LCD_EN 2
unsigned char received_data,count = 0,inc = 0;
char received_string[100];
void LCD_cmnd(unsigned char cmnd)
{
	LCD_DATAPORT=cmnd;
	LCD_CMNDPORT &= ~(1<<LCD_RS);
	LCD_CMNDPORT &= ~(1<<LCD_RW);
	LCD_CMNDPORT |= (1<<LCD_EN);
	_delay_us(5);
	LCD_CMNDPORT &= ~(1<<LCD_EN);
	_delay_us(200);
}
void LCD_data(unsigned char data)
{
	LCD_DATAPORT = data;
	LCD_CMNDPORT |= (1<<LCD_RS);
	LCD_CMNDPORT &= ~(1<<LCD_RW);
	LCD_CMNDPORT |= (1<<LCD_EN);
	_delay_us(5);
	LCD_CMNDPORT &= ~(1<<LCD_EN);
	_delay_us(200);
}
void LCD_initialize(void)
{
	LCD_DATADDR = 0xFF;
	LCD_CMNDDDR = 0xFF;
	LCD_CMNDPORT &= ~(1<<LCD_EN);
	_delay_ms(20);
	LCD_cmnd(0x38);
	_delay_ms(20);
	LCD_cmnd(0x0E);
	_delay_ms(20);
	LCD_cmnd(0x01);
	_delay_ms(20);
}
void LCD_clear(void)
{
	LCD_cmnd(0x01);
	_delay_ms(2);
}
void LCD_print(char * str)
{
	unsigned char i=0;
	while(str[i] != 0)
	{
		LCD_data(str[i]);
		i++;
		_delay_ms(5);
	}
}
void LCD_set_curser(unsigned char y, unsigned char x)
{
	if(y==1)
	LCD_cmnd(0x7F+x);
	else if(y==2)
	LCD_cmnd(0xBF+x);
}
void LCD_num(unsigned char num)
{
	//LCD_data(num/100 + 0x30);
	//num = num%100;
	LCD_data(num/10 + 0x30);
	LCD_data(num%10 + 0x30);
}

void usart_initialize()
{
	UCSRB = 1<<RXEN;
	UCSRC = (1<<UCSZ0)|(1<<UCSZ1)|(1<<URSEL);
	UBRRL = 0x67;
}
void usart_receive()
{
	while(!(UCSRA&(1<<RXC)));
	received_string[inc] = UDR;
	inc++;
	count ++;
}
int main(void)
{
	while(1) {
	unsigned char i;
	LCD_initialize();
	usart_initialize();
	LCD_cmnd(0x0C);
	count = 0;
	while(1)
    {
		usart_receive();
		if (count == 99) break;
    }
	LCD_print("SMS Received:");
	_delay_ms(500);
	LCD_clear();
	for (i=47;i<63;i++)
	{
		LCD_data(received_string[i]);
	}
	LCD_set_curser(2,1);
	for (i=64;i<82;i++)
	{
		LCD_data(received_string[i]);
	}
	_delay_ms(1000);
	LCD_clear();
	for (i=82;i<99;i++)
	{
		LCD_data(received_string[i]);
	}
	_delay_ms(2000);
	LCD_clear();
	}
}