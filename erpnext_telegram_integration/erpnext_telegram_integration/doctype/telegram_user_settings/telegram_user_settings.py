# -*- coding: utf-8 -*-
# Copyright (c) 2019, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import binascii
import os
from frappe.model.document import Document
from frappe import _


class TelegramUserSettings(Document):
	

	def validate(self):
		pass


	def get_token_settings(self):
		return frappe.db.get_value('Telegram Settings', self.telegram_settings,'telegram_token')


	def get_chat_id(self):
		telegram_token_bot = self.get_token_settings()
		self.telegram_chat_id = get_chat_id(telegram_token_bot, self.telegram_token)




@frappe.whitelist()
def generate_telegram_token(is_group_chat):
	if int(is_group_chat) == 1:
		return "/"+ binascii.hexlify(os.urandom(19)).decode()
	else:
		return binascii.hexlify(os.urandom(20)).decode()

@frappe.whitelist()
def get_chat_id_button(telegram_token, telegram_settings):
	telegram_token_bot = frappe.db.get_value('Telegram Settings', telegram_settings,'telegram_token')
	chat_id = get_chat_id(telegram_token_bot, telegram_token)
	if chat_id:
		return str(chat_id)
	else:
		frappe.msgprint(_("No chat id found for this token, please check the token and make sure you are pasting it in the right chat boot or group in Telegram"))

def get_chat_id(telegram_token_bot, telegram_token):
	response = requests.get(
		f"https://api.telegram.org/bot{telegram_token_bot}/getUpdates",
		params={"limit": 100},
		timeout=30,
	)
	response.raise_for_status()
	for u in response.json().get("result", []):
		msg = u.get("message")
		# ignore messages without text
		if not msg or not msg.get("text"):
			continue
		if telegram_token == msg["text"]:
			chat_id = msg["chat"]["id"]
			print("chat_id >>>>>> " + str(chat_id))
			return chat_id