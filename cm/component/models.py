from django.db import models
from django.core.exceptions import ValidationError

# Component model based on Edge-Weighted Directed Acyclic Graph

class AbstractComponent(models.Model):
    name = models.CharField(
        max_length=20,
    )


class Component(AbstractComponent):
    class TypeTag(models.IntegerChoices):
        Part = 0
        Assembly = 1
    
    type_tag = models.IntegerField(
        choices=TypeTag.choices,
    )

    part_only_data = models.TextField(
        blank=True,
    )

    sub_components = models.ManyToManyField(
        to="self",
        through="ComponentRelation",
        blank=True,
        related_name="super_components",
        symmetrical=False,
    )

    assembly_only_data = models.TextField(
        blank=True
    )

    def __str__(self) -> str:
        return self.name

    def get_number_of_parts(self) -> int:
        if self.type_tag == self.TypeTag.Part:
            return 1
        elif self.type_tag == self.TypeTag.Assembly:
            return sum(
                list(
                    map(
                        lambda x: 
                        x.to_component.get_number_of_parts() * x.weight,
                         ComponentRelation.objects.filter(from_component = self),
                    )
                )
            )
    get_number_of_parts.short_description = "Number of Parts"

class ComponentRelation(models.Model):
    from_component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="sub_relation",
    )
    to_component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="super_relation",
    )
    weight = models.IntegerField()

    class Meta:
        # Validate no parallel edge
        unique_together = (
            "from_component",
            "to_component",
        )

    def is_acyclic_(self, ref, object) -> bool:
        if object.pk != ref.pk:
            sub_components = object.sub_components.all()
            if not sub_components:
                return True
            else:
                return all(
                    list(
                        map(
                            lambda x:
                            self.is_acyclic_(
                                ref,
                                Component.objects.get(pk=x.pk)
                            ),
                            sub_components,
                        )
                    )
                )
        else:
            return False

    # Validate no self-referencing node, and acyclicity
    def is_acyclic(self) -> bool:
        return self.is_acyclic_(self.from_component, self.to_component)

    def is_from_assembly(self) -> bool:
        return self.from_component.type_tag == Component.TypeTag.Assembly

    def clean(self) -> None:
        super().clean()
        # Validate no self-referencing node, and acyclicity
        if not self.is_acyclic():
            # todo Present cyclic path for convenience 
            raise ValidationError("Cyclic component definition is not permitted.")
        
        # Validate if the type of parent component is Assembly
        if not self.is_from_assembly():
            raise ValidationError("Type of parent component should be Assembly, not Part.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
