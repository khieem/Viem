import base64
import re
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
EC = ec.SECP256R1()

class Crypto:

	def _modular_inverse(self, a, b):
		_b = b
		x1,x2, y1,y2 = 0,1,1,0
		while b != 0:
			q, r = a//b, a%b
			x, y = x2-x1*q, y2-y1*q
			a, b, x2,x1, y2,y1 = b,r,x1,x,y1,y
		if x2 != 0: x2 = x2+_b
		return x2

	def _modular_exponentiation(self, b, n, m):
		n = bin(n)
		x = 1
		power = b%m
		for i in range(len(n)-1, 1, -1):
			if n[i] == '1': x = (x*power)%m
			power = (power*power) % m
		return x

	def _add_point(self, a, b, p, Px, Py, Qx, Qy):
		if Px == Qx and Py == p-Qy:
			return float('inf'), float('inf')
		elif Px == Qx and Py == Qy:
			ld = ( (3*Px*Px + a) * self._modular_inverse(2*Py,p) )%p
		elif Px != Qx:
			ld = ((Qy-Py) * self._modular_inverse(Qx-Px,p))%p
		x3 = (p+ ld*ld - Px - Qx)%p
		return x3, (p+ld*(Px - x3) - Py)%p

	def _double_and_add(self, a, b, p, Px, Py, d):
		d = bin(d)
		Tx = Px
		Ty = Py
		for i in range(len(d)-1, 0, -1):
			Tx, Ty = self._add_point(a, b, p, Tx, Ty, Tx, Ty)
			if d[i] == '1': Tx, Ty = self._add_point(a, b, p, Tx, Ty, Px, Py)
		return Tx, Ty


	def _generate_points(self, a, b, p, x1, y1):
		elliptic = []
		elliptic.append((x1,y1))
		elliptic.append((x1,y1))

		while True:
			x2, y2 = elliptic[-1]
			if x2 == float('inf'): break
			x3, y3 = self._add_point(a,b,p,x1,y1,x2,y2)
			elliptic.append((x3,y3))
		return elliptic[1:]

	def _proc(self, expression):
		bieu_thuc = expression
		if bieu_thuc == 'exit':
			pass
		gcd_pattern = 'gcd'
		modular_pattern = 'mod'

		a = re.search(modular_pattern, bieu_thuc)
		if a != None:
			e1 = re.search('^\d+', bieu_thuc)
			a = int(e1.group())

			em = re.search('\d+$', bieu_thuc)
			m = int(em.group())

			eb = re.search('-1', bieu_thuc)
			if eb == None:
				b = int(re.search('\^\d+', bieu_thuc).group()[1:])
				return (self._modular_exponentiation(a, b, m))
			else:
				return (self._modular_inverse(a, m))

	def to_bytes(self, EllipticCurveKeyObject):
		if isinstance(EllipticCurveKeyObject, ec.EllipticCurvePublicKey):
			return EllipticCurveKeyObject.public_bytes(
						encoding=serialization.Encoding.PEM,
						format=serialization.PublicFormat.SubjectPublicKeyInfo
			)
		else:
			return EllipticCurveKeyObject.private_bytes(
						encoding=serialization.Encoding.PEM,
						format=serialization.PrivateFormat.PKCS8, 
						encryption_algorithm=serialization.NoEncryption()
			)

	def generate_private_key(self):
		pk = ec.generate_private_key(EC, default_backend())
		return pk

	def load_private_key(self, bytestream):
		return serialization.load_pem_private_key(bytestream, password=None, backend=default_backend())
	
	def load_public_key(self, bytestream):
		return serialization.load_pem_public_key(bytestream, backend=default_backend())

	def show_hex_key(self, EllipticCurvePrivateKeyObject):
		print(self.to_bytes(EllipticCurvePrivateKeyObject).hex())

	def exchange_key(self, EllipticCurvePrivateKeyObject, EllipticCurvePublicKeyObject):
		return EllipticCurvePrivateKeyObject.exchange(ec.ECDH(), EllipticCurvePublicKeyObject)

	def _encrypt(self, message, bytestream_key):
		kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
								length=32,
								salt = b'ec.CGK5x.ppSalt_',
								iterations=54436,
								backend=default_backend())
		key = base64.urlsafe_b64encode(kdf.derive(bytestream_key))		
		secrets.randbits(32)
		message = message.encode() if isinstance(message, str) else message
		fernet = Fernet(key)
		encrypted_bytestream = fernet.encrypt(message) 
		return encrypted_bytestream

	def _decrypt(self, encrypted_bytestream, bytestream_key):
		kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
								length=32,
								salt = b'ec.CGK5x.ppSalt_',
								iterations=54436,
								backend=default_backend())
		key = base64.urlsafe_b64encode(kdf.derive(bytestream_key))
		fernet = Fernet(key)
		decrypted_bytestream = fernet.decrypt(encrypted_bytestream) 
		return decrypted_bytestream


if __name__ == '__main__':

	with open('pub_key.perm', 'rb') as key_file: 
	   public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())

	pub_der = public_key.public_bytes(
	   encoding=serialization.Encoding.DER,
	   format=serialization.PublicFormat.SubjectPublicKeyInfo
	)
