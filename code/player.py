from entity import Entity
import pygame
from support import import_folder 
from settings import *

class Player(Entity):
	def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_magic):
		super().__init__(groups)
		self.image = pygame.image.load(BASEDIR+'/graphics/test/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-26)
		
		#graphics
		self.import_player_assets()
		self.status = 'down'
		

		# vector for player movement direction
		self.obstacle_sprites = obstacle_sprites
		
		# movement
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None
		self.destroy_attack = destroy_attack
		
		# weapon
		self.create_attack = create_attack  # this makes the weapon method available to player
		self.weapon_index = 0
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 200 

		# magic
		self.create_magic = create_magic
		self.magic_index = 0
		self.magic = list(magic_data.keys())[self.magic_index]
		self.can_switch_magic = True
		self.magic_switch_time = None
		

		# player
		# dictionary of player max stats
		self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
		# individual values for current stats
		self.health = self.stats['health']
		self.energy = self.stats['energy']
		self.speed = self.stats['speed']
		self.exp = 123

	def get_status(self):

		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = self.status + '_idle'
		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_attack')
				else:
					self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack','')

	def input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			self.direction.y = -1
			self.status = 'up'
		elif keys[pygame.K_DOWN]:
			self.direction.y = 1
			self.status = 'down'
		# reset if key is released
		else:
			self.direction.y = 0

		if keys[pygame.K_LEFT]:
			self.direction.x = -1
			self.status = 'left'
		elif keys[pygame.K_RIGHT]:
			self.direction.x = 1
			self.status = 'right'
		# reset if key is released
		else:
			self.direction.x = 0


		# attack input
		if keys[pygame.K_SPACE] and not self.attacking:
			self.attacking = True
			self.attack_time = pygame.time.get_ticks()
			self.create_attack()

		if keys[pygame.K_LCTRL] and not self.attacking:
			self.attacking = True
			self.attack_time = pygame.time.get_ticks()
			style = list(magic_data.keys())[self.magic_index]
			cost = list(magic_data.values())[self.magic_index]['cost']
			strength =list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
			self.create_magic(style,cost,strength)

		if keys[pygame.K_q] and self.can_switch_weapon:
			if self.weapon_index < len(list(weapon_data.keys())) - 1:
				self.weapon_index += 1
			else:
				self.weapon_index = 0
			self.weapon = list(weapon_data.keys())[self.weapon_index]
			self.can_switch_weapon = False
			self.weapon_switch_time = pygame.time.get_ticks()
		
		if keys[pygame.K_e] and self.can_switch_magic:
			if self.magic_index < len(list(magic_data.keys())) - 1:
				self.magic_index += 1
			else:
				self.magic_index = 0
			self.magic = list(magic_data.keys())[self.magic_index]
			self.can_switch_magic = False
			self.magic_switch_time = pygame.time.get_ticks()

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attacking = False
				self.destroy_attack()
		
		if not self.can_switch_weapon:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True

		if not self.can_switch_magic:
			if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
				self.can_switch_magic = True
					
	def import_player_assets(self):
		character_path = BASEDIR + 'graphics/player/'
		self.animations = {'up':[],'down':[],'left':[],'right':[],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]
		}

		for animations in self.animations.keys():
			full_path = character_path + animations
			self.animations[animations] = import_folder(full_path)
	
	def animate(self):
		animation = self.animations[self.status]

		#loop over frame index
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set the image
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

	def update(self):
		self.input()
		self.move(self.speed)
		self.cooldowns()
		self.get_status()
		self.animate()
