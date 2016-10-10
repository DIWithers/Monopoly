from flask import Flask
from flaskext.mysql import MySQL
import random

app = Flask(__name__)
mysql = MySQL()
#Add to the app (flask object) some config data for our connection
#config is a dictionary
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
app.config['MYSQL_DATABASE_DB'] = 'monopoly'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
#use the mysql object's method "init_app" and pass it the flask object
mysql.init_app(app)

#Make one re-usable connection
conn = mysql.connect()
#set up cursor object which sql can use and run queries
cursor = conn.cursor()




def roll():
	dbl = 0
	d1 = random.randrange(1, 6)
	d2 = random.randrange(1, 6)
	total_roll = d1 + d2
	if d1 == d2: 
		dbl = 1
	return [d1, d2, total_roll, dbl]

def game_start():
	print "*********************** WELCOME TO MONOPOLY!!!! ********************************"

	game_reset = raw_input("Erase prior game data? Y/N ")
	if game_reset == "Y":
		delete_query = "DELETE from moves"
		cursor.execute(delete_query)
		delete_query = "DELETE from players"
		cursor.execute(delete_query)
		delete_query = "DELETE from rolls"
		cursor.execute(delete_query)
	else:
		print "Continuing stats from prior game"

	#init players
	p1_name = raw_input("Enter Player 1's name: ")
	init_player_query = "INSERT INTO players VALUES (DEFAULT, %s, '1')"
	cursor.execute(init_player_query, (p1_name))
	playerQ = cursor.fetchone()
	print playerQ
	conn.commit()

	p2_name = raw_input("Enter Player 2's name: ")
	init_player_query = "INSERT INTO players VALUES (DEFAULT, %s, '2')"
	cursor.execute(init_player_query, (p2_name))
	conn.commit()


	turnCount = 0
	p1_isTurn = True
	p2_isTurn = False
	p1_landing_square_id = 1
	p2_landing_square_id = 1
	p1_jail_status = 0
	p2_jail_status = 0
	p1_bailCount = 0
	p2_bailCount = 0

	while turnCount <= 1000:

		if p1_isTurn == True:
			if p1_jail_status != "V" or p1_jail_status != 1:
				p1_roll = roll()
				dice1 = p1_roll[0]
				dice2 = p1_roll[1]
				total_roll = p1_roll[2]
				isDouble = p1_roll[3]

				roll_query = "INSERT INTO rolls VALUES (DEFAULT, '1', %s, %s, %s, %s)" % (dice1, dice2, total_roll, isDouble)
				# print roll_query
				cursor.execute(roll_query)
				rollP1 = cursor.fetchone()

				conn.commit()
				
				p1_landing_square_id += p1_roll[2] #MOVES
				print "Player 1:" + str(p1_roll) + "SQ ID= " + str(p1_landing_square_id)

				if p1_landing_square_id == 11: # Visiting Jail!
					p1_jail_status = "V"
					print "Player One visits jail for one turn!"


				if p1_landing_square_id == 30: # IN JAIL!!!
					p1_jail_status = 1
					print "Player One is in jail!"

				if p1_landing_square_id > 39: # player passed GO
					p1_landing_square_id -= 39
					print "PLAYER ONE PASSED GO to " + str(p1_landing_square_id)

				moves_query = "INSERT INTO moves VALUES(DEFAULT, '1', %s)"
				cursor.execute(moves_query, (p1_landing_square_id))

				if p1_jail_status != "V" or p1_jail_status != 1:
					if p1_roll[3] == 1: #roll again!
						p1_roll = roll()
						print "Player 1:" + str(p1_roll) + "SQ ID= " + str(p1_landing_square_id)
						roll_query = "INSERT INTO rolls VALUES (DEFAULT, '1', %s, %s, %s, %s)" % (dice1, dice2, total_roll, isDouble)
						# print roll_query
						cursor.execute(roll_query)
						rollP1 = cursor.fetchone()
						# print rollP1
						conn.commit()
					p1_isTurn = False
					p2_isTurn = True
					turnCount += 1

			if p1_jail_status == "V": #Only visiting, skip one turn
				p1_isTurn = False
				p2_isTurn = True
				p1_jail_status = 0
				turnCount += 1

			if p1_jail_status == 1:
				
				if p1_bailCount < 3:
					bailRoll = roll()
					p1_bailCount += 1
					if bailRoll[2] == 1: #rolled a double! FREEDOM!!!
						p1_isTurn = False
						p2_isTurn = True
						p1_jail_status = 0
						turnCount += 1
						p1_bailCount = 0
					else:
						p1_isTurn = False #Bail denied
						p2_isTurn = True
						turnCount += 1
				else: # Out of jail on 3 turns
					p1_isTurn = False
					p2_isTurn = True
					p1_jail_status = 0
					turnCount += 1
					p1_bailCount = 0



		else:
			if p2_jail_status != "V" or p2_jail_status != 1:
				p2_roll = roll()

				dice1 = p2_roll[0]
				dice2 = p2_roll[1]
				total_roll = p2_roll[2]
				isDouble = p2_roll[3]

				roll_query = "INSERT INTO rolls VALUES (DEFAULT, '2', %s, %s, %s, %s)" % (dice1, dice2, total_roll, isDouble)
				# print roll_query
				cursor.execute(roll_query)
				conn.commit()
				p2_landing_square_id += p2_roll[2] #moves
				print "Player 2:" + str(p2_roll) + "SQ ID= " + str(p2_landing_square_id)

				if p2_landing_square_id == 11: # Visiting Jail!
					p2_jail_status = "V"
					print "Player Two visits jail for one turn!"

				if p2_landing_square_id == 30: # IN JAIL!!!
					p2_jail_status = 1
					print "Player Two is in Jail!"

				if p2_landing_square_id > 39: #moves if passes go
					p2_landing_square_id -= 39
					print "PLAYER TWO PASSED GO to " + str(p2_landing_square_id)
				moves_query = "INSERT INTO moves VALUES(DEFAULT, '2', %s)"
				cursor.execute(moves_query, (p2_landing_square_id))

				
				if p2_roll[3] == 1: #roll again!
					p2_roll = roll()
					print "Player 2:" + str(p2_roll) + "SQ ID= " + str(p2_landing_square_id)
					roll_query = "INSERT INTO rolls VALUES (DEFAULT, '2', %s, %s, %s, %s)" %(dice1, dice2, total_roll, isDouble)
					# print roll_query
					cursor.execute(roll_query)
					conn.commit()
				p2_isTurn = False
				p1_isTurn = True
				turnCount += 1

			if p2_jail_status == "V": #Only visiting, skip one turn
				p2_isTurn = False
				p1_isTurn = True
				p2_jail_status = 0
				turnCount += 1

			if p2_jail_status == 1:
				
				if p2_bailCount < 3:
					bailRoll = roll()
					p2_bailCount += 1
					if bailRoll[2] == 1: #rolled a double! FREEDOM!!!
						p2_isTurn = False
						p1_isTurn = True
						p2_jail_status = 0
						turnCount += 1
						p2_bailCount = 0
					else:
						p2_isTurn = False #Bail denied
						p1_isTurn = True
						turnCount += 1
				else: # Out of jail on 3 turns
					p2_isTurn = False
					p1_isTurn = True
					p2_jail_status = 0
					turnCount += 1
					p2_bailCount = 0

	








game_start()



if __name__ == "__main__":
	app.run(debug=True)