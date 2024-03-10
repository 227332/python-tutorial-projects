from confluent_kafka.serialization import SerializationContext


class Product:
    def __init__(self, product_name: str):
        self._product_name = product_name

    @property
    def product_name(self) -> str:
        return self._product_name

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}(product_name={self.product_name})"


def product_to_dict(product: Product, ctx: SerializationContext) -> dict[str, str]:
    return {"product_name": product.product_name}


def dict_to_product(product_dict: dict[str, str], ctx: SerializationContext) -> Product:
    return Product(product_name=product_dict["product_name"])


schema_str = """{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Message",
    "description": "Message with product info",
    "type": "object",
    "properties": {
        "product": {
            "description": "Product name",
            "type": "string"
        }
    }
}"""
