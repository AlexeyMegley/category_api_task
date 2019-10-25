from django.db import models

# Create your models here.
class Category(models.Model):

	name = models.CharField(max_length=255, unique=True)
	children = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='parents')

	def __str__(self):
		return self.name

	def get_info_dict(self):
		return {'id': self.pk, 'name': self.name}

	def extract_relations_dict(self) -> dict:
		closest_parents = self.parents.all()
		children = list(self.children.values('id', 'name'))
		siblings = [child.get_info_dict() for parent in closest_parents for child in parent.children.all() if child != self]
		parents = self.extract_all_parents(closest_parents, include_initial=True)
		return {
				'id': self.pk,
				'name': self.name,
				'parents': [parent.get_info_dict() for parent in parents],
				'children': children,
				'siblings': siblings
			   }

	@classmethod
	def extract_all_parents(cls, qs, include_initial=True):
		relatives_hierarchy = list(qs) if include_initial else []
		next_gen = {parent for element in relatives_hierarchy for parent in element.parents.all()}
		while next_gen:
			relatives_hierarchy += list(next_gen)
			next_gen = {parent for element in next_gen for parent in element.parents.all()}
		
		return relatives_hierarchy

