from django.db import models
import django.utils.timezone as timezone
from team.models import Department
from user.models import User


class Position(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300, unique=True, verbose_name="岗位名称")
    score = models.FloatField(verbose_name="岗位基础分数")
    workload = models.FloatField(verbose_name="岗位基础工作量")
    bonus = models.FloatField(verbose_name="岗位基础奖金")

    class Meta:
        verbose_name = '岗位'
        verbose_name_plural = "岗位"

    def __str__(self):
        return self.name


class SkillType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="技能类别")

    class Meta:
        verbose_name = '技能类别'
        verbose_name_plural = "技能类别"

    def __str__(self):
        return self.name


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(SkillType, on_delete=models.CASCADE, verbose_name="技能类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="技能名称")
    score = models.FloatField(verbose_name="技能基础分数")
    workload = models.FloatField(verbose_name="技能基础工作量")
    bonus = models.FloatField(verbose_name="技能基础奖金")

    class Meta:
        verbose_name = '技能'
        verbose_name_plural = "技能"

    def __str__(self):
        return self.name


class RewardType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="奖惩类别")

    class Meta:
        verbose_name = '奖惩类别'
        verbose_name_plural = "奖惩类别"

    def __str__(self):
        return self.name


class Reward(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(RewardType, on_delete=models.CASCADE, verbose_name="奖惩类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="奖惩名称")
    score = models.CharField(max_length=100, verbose_name="奖惩基础分")
    workload = models.FloatField(verbose_name="奖惩基础工作量")
    bonus = models.FloatField(verbose_name="奖惩基础奖金")

    class Meta:
        verbose_name = '奖惩'
        verbose_name_plural = "奖惩"

    def __str__(self):
        return self.name


class ShiftType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="班次类别")

    class Meta:
        verbose_name = '班次类别'
        verbose_name_plural = "班次类别"

    def __str__(self):
        return self.name


class Shift(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(ShiftType, on_delete=models.CASCADE, verbose_name="班次类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="班次")
    score = models.CharField(max_length=100, verbose_name="班次基础分")
    workload = models.FloatField(verbose_name="班次基础工作量")
    bonus = models.FloatField(verbose_name="班次基础奖金")

    class Meta:
        verbose_name = '班次'
        verbose_name_plural = "班次"

    def __str__(self):
        return self.name


class Rule(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="名称")

    class Meta:
        verbose_name = '规则'
        verbose_name_plural = "规则"

    def __str__(self):
        return self.name


class AddWorkload(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="user", on_delete=models.DO_NOTHING, verbose_name="登记人")
    position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, verbose_name="岗位")
    worktime = models.CharField(max_length=1000, verbose_name="工作时长")
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, verbose_name="指派分队")
    created_time = models.CharField(max_length=100, verbose_name="工作量所属日期")
    remark = models.CharField(max_length=1000, verbose_name="备注")
    updated_time = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="登记日期")

    class Meta:
        verbose_name = '工作量登记'
        verbose_name_plural = "工作量登记"

    def __str__(self):
        return self.id


class Score(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, to_field="id", related_name="employee",
                                    verbose_name="员工姓名")
    # position_name = models.ManyToManyField(Position, verbose_name="岗位")
    # # position_staff_score = models.FloatField(max_length=1000, verbose_name="岗位工作量")
    # shift_name = models.ManyToManyField(Shift, verbose_name="班次")
    skill_score = models.FloatField(max_length=1000, verbose_name="技能分数")
    penalty_score = models.FloatField(max_length=1000, verbose_name="奖惩得分")
    po_score = models.FloatField(max_length=1000, verbose_name="岗位分数")
    total_score = models.FloatField(max_length=1000, verbose_name="总分")
    date = models.DateField(default=timezone.now, verbose_name="日期")
    remark = models.TextField(max_length=1000, blank=True, null=True, verbose_name="备注")

    class Meta:
        verbose_name = '统计'
        verbose_name_plural = "统计"
