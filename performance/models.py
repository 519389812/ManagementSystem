from django.db import models
import django.utils.timezone as timezone
from user.models import User
from team.models import Team


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="程度名称")

    class Meta:
        verbose_name = '程度'
        verbose_name_plural = "程度"

    def __str__(self):
        return self.name


class RuleCondition(models.Model):
    id = models.AutoField(primary_key=True)
    reference = models.CharField(max_length=100, unique=True, verbose_name="参照")
    symbol = models.CharField(max_length=100, verbose_name="符号")
    case = models.CharField(max_length=100, verbose_name="条件")

    class Meta:
        verbose_name = '规则类别'
        verbose_name_plural = "规则类别"

    def __str__(self):
        return self.id


class Rule(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="名称")
    condition = models.ManyToManyField(RuleCondition, verbose_name="条件")
    calculation = models.CharField(max_length=100, verbose_name="计算方法")

    class Meta:
        verbose_name = '规则'
        verbose_name_plural = "规则"

    def __str__(self):
        return self.name


class PositionType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="岗位类别")

    class Meta:
        verbose_name = '岗位类别'
        verbose_name_plural = "岗位类别"

    def __str__(self):
        return self.name


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
    rule = models.ManyToManyField(Rule)

    class Meta:
        verbose_name = '班次'
        verbose_name_plural = "班次"

    def __str__(self):
        return self.name


class AddWorkload(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="登记人")
    shift = models.ForeignKey(Shift, on_delete=models.DO_NOTHING, verbose_name="班次")
    position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, verbose_name="岗位")
    start_datetime = models.DateTimeField(verbose_name="开始时间")
    end_datetime = models.DateTimeField(verbose_name="结束时间")
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, verbose_name="指派")
    remark = models.TextField(max_length=1000, verbose_name="备注")
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name="登记时间")
    verified = models.BooleanField(verbose_name="审核状态")
    verified_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="审核人")
    verified_datetime = models.DateTimeField(blank=True, verbose_name="审核时间")

    class Meta:
        verbose_name = '工作量'
        verbose_name_plural = "工作量"

    def __str__(self):
        return self.id


class ReferenceType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="类型名称")

    class Meta:
        verbose_name = '涉及类别'
        verbose_name_plural = "涉及类别"

    def __str__(self):
        return self.name


class Reference(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(ReferenceType, on_delete=models.CASCADE, verbose_name="涉及类别")
    name = models.CharField(max_length=100, unique=True, verbose_name="涉及内容")

    class Meta:
        verbose_name = '涉及'
        verbose_name_plural = "涉及"

    def __str__(self):
        return self.name


class AddReward(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="责任人")
    date = models.DateTimeField(verbose_name="日期")
    reward = models.ForeignKey(Reward, on_delete=models.DO_NOTHING, verbose_name="奖惩")
    reference = models.ManyToManyField(Reference, verbose_name="涉及内容")
    title = models.CharField(max_length=500, verbose_name="标题")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name="影响程度")
    content = models.TextField(max_length=1000, verbose_name="详细情况")
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name="登记时间")
    created_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="登记人")

    class Meta:
        verbose_name = '工作量登记'
        verbose_name_plural = "工作量登记"

    def __str__(self):
        return self.id
