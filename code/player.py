import pygame
from support import import_folder 
from settings import *

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,groups,obstacle_sprites):
		super().__init__(groups)
		self.image = pygame.image.load('/Users/fitz/CODE/Python/Zelda-like/graphics/test/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-26)
		
		#graphics
		self.import_player_assets()
		self.status = 'down'
		self.frame_index = 0
		self.animation_speed = 0.15

		# vector for player movement direction
		self.direction = pygame.math.Vector2()
		self.speed = 5
		self.obstacle_sprites = obstacle_sprites
		
		# movement
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None

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
			print('attacking')
			self.attacking = True
			self.attack_time = pygame.time.get_ticks()

		if keys[pygame.K_LCTRL] and not self.attacking:
			print('attacking')
			self.attacking = True
			self.attack_time = pygame.time.get_ticks()

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attacking = False

	def move(self, speed):
		# this helps to account for angular movement
		# if statement just makes sure we don't have an angle of zero, would cause an error
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
		
		self.hitbox.x += self.direction.x * speed
		self.collision('horizonal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hitbox.center

	def collision(self,direction):
		if direction == 'horizonal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0: # moving right
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0: # moving left
						self.hitbox.left = sprite.hitbox.right


		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0: # moving down
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0: # moving up
						self.hitbox.top = sprite.hitbox.bottom
						
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
