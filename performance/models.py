from django.db import models
import django.utils.timezone as timezone
from user.models import User
from team.models import Team
from django.contrib import admin


class Rule(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="名称")
    condition = models.CharField(max_length=100, verbose_name="条件")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '规则'
        verbose_name_plural = " 规则"

    def __str__(self):
        return self.name


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="程度名称")
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, null=True, blank=True, verbose_name="规则")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '程度'
        verbose_name_plural = "  程度"

    def __str__(self):
        return self.name


class PositionType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="岗位类别")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '岗位类别'
        verbose_name_plural = "   岗位类别"

    def __str__(self):
        return self.name


class Position(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(PositionType, on_delete=models.CASCADE, verbose_name="岗位类别")
    name = models.CharField(max_length=300, unique=True, verbose_name="岗位名称")
    score = models.FloatField(verbose_name="岗位基础分数")
    workload = models.FloatField(verbose_name="岗位基础工作量")
    bonus = models.FloatField(verbose_name="岗位基础奖金")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '岗位'
        verbose_name_plural = "    岗位"

    def __str__(self):
        return self.name


class SkillType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="技能类别")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '技能类别'
        verbose_name_plural = "     技能类别"

    def __str__(self):
        return self.name


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(SkillType, on_delete=models.CASCADE, verbose_name="技能类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="技能名称")
    score = models.FloatField(verbose_name="技能基础分数")
    workload = models.FloatField(verbose_name="技能基础工作量")
    bonus = models.FloatField(verbose_name="技能基础奖金")
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, null=True, blank=True, verbose_name="规则")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '技能'
        verbose_name_plural = "      技能"

    def __str__(self):
        return self.name


class RewardType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="奖惩类别")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '奖惩类别'
        verbose_name_plural = "       奖惩类别"

    def __str__(self):
        return self.name


class Reward(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(RewardType, on_delete=models.CASCADE, verbose_name="奖惩类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="奖惩名称")
    score = models.FloatField(verbose_name="奖惩基础分")
    workload = models.FloatField(verbose_name="奖惩基础工作量")
    bonus = models.FloatField(verbose_name="奖惩基础奖金")
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, null=True, blank=True, verbose_name="规则")
    team = models.ForeignKey(Team, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '奖惩'
        verbose_name_plural = "        奖惩"

    def __str__(self):
        return self.name


class ShiftType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="班次类别")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '班次类别'
        verbose_name_plural = "         班次类别"

    def __str__(self):
        return self.name


class Shift(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(ShiftType, on_delete=models.CASCADE, verbose_name="班次类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="班次")
    score = models.FloatField(verbose_name="班次基础分")
    workload = models.FloatField(verbose_name="班次基础工作量")
    bonus = models.FloatField(verbose_name="班次基础奖金")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '班次'
        verbose_name_plural = "          班次"

    def __str__(self):
        return self.name


class ReferenceType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="类型名称")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '涉及类别'
        verbose_name_plural = "           涉及类别"

    def __str__(self):
        return self.name


class Reference(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(ReferenceType, on_delete=models.CASCADE, verbose_name="涉及类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="涉及内容名称")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name="目标组")

    class Meta:
        verbose_name = '涉及内容'
        verbose_name_plural = "            涉及内容"

    def __str__(self):
        return self.name


class AddReward(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='reward_user', on_delete=models.CASCADE, verbose_name="责任人")
    date = models.DateTimeField(verbose_name="日期")
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, verbose_name="奖惩")
    reference = models.ManyToManyField(Reference, verbose_name="涉及内容")
    title = models.CharField(max_length=500, verbose_name="标题")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name="影响程度")
    content = models.TextField(max_length=1000, blank=True, verbose_name="详细情况")
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name="登记时间")
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="登记人")

    class Meta:
        verbose_name = '奖惩记录'
        verbose_name_plural = "             奖惩记录"

    def __str__(self):
        return str(self.id)


class AddWorkload(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='workload_user', on_delete=models.CASCADE, verbose_name="登记人")
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="班次")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="岗位")
    start_datetime = models.DateTimeField(verbose_name="开始时间")
    end_datetime = models.DateTimeField(verbose_name="结束时间")
    assigned_team = models.ForeignKey(Team, related_name='assigned_team', on_delete=models.CASCADE, verbose_name="指派")
    remark = models.TextField(max_length=1000, blank=True, verbose_name="备注")
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name="登记时间")
    verified = models.BooleanField(default=False, verbose_name="审核状态")
    verified_user = models.ForeignKey(User, blank=True, related_name='verified_user', on_delete=models.CASCADE, verbose_name="审核人")
    verified_datetime = models.DateTimeField(blank=True, verbose_name="审核时间")

    class Meta:
        verbose_name = '工作量记录'
        verbose_name_plural = "              工作量记录"

    def __str__(self):
        return str(self.id)
