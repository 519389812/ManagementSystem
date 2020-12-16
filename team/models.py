from django.db import models


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name="名称")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="上级部门")
    related_parent = models.CharField(max_length=300, verbose_name="组织关系")

    class Meta:
        verbose_name = "分组"
        verbose_name_plural = "分组"

    def get_related_parent(self):
        related_parent = [self.id]
        if self.parent:
            parent = self.parent
            while True:
                try:
                    related_parent.insert(0, parent.id)
                    parent = parent.parent
                except:
                    break
        return str(related_parent)

    def get_related_parent_name(self):
        related_parent_id_list = list(self.get_related_parent())
        related_parent_name = '-->'.join([Team.objects.get(id=id).name for id in related_parent_id_list])
        return related_parent_name

    def __str__(self):
        return self.get_related_parent_name()
