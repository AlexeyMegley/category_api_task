from rest_framework.test import APITestCase, force_authenticate
from rest_framework import status
from rest_framework.reverse import reverse
from django.contrib.auth.models import User

from .models import Category


class CategoryTests(APITestCase):

    def setUp(self):
        super().setUp()
        self.base_url = reverse('category:categories-list')

    def test_simple_cases(self):
        data = {
            "name": "1",
            "children": [
                {
                 "name": "1.1",
                 "children": [
                     {
                         "name": "1.1.1"
                     }
                 ]
                },
                {
                    "name": "1.2"
                }
            ]
        }
        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        categories = Category.objects.filter(name__in=("1", "1.1", "1.1.1", "1.2"))
        self.assertEqual(categories.count(), 4)

        for category in categories:
            response = self.client.get(reverse('category:categories-detail', [category.pk]))
            self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_wo_children(self):
        data = {
            "name": "1",
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        category = Category.objects.get(name="1")
        response = self.client.get(reverse('category:categories-detail', [category.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_wo_name(self):
        data = {
            "name": "1",
            "children": [
                {
                    "name": ""
                }
            ]
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_name_already_exists(self):
        data = {
            "name": "1.1"
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "name": "1",
            "children": [
                {
                    "name": "1.1"
                }
            ]
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Try more complex one
        data = {
            "name": "2",
            "children": [
                {
                    "name": "2.1",
                    "children": [
                         {
                             "name": "2.1.1"
                         },
                         {
                             "name": "2.1.2",
                             "children": [
                                 {"name": "2"}
                             ]
                         }

                    ]
                }
            ]
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_format(self):
        data = {
            "name": "1",
            "children": ["1.1", "1.2", "1.3"]
        }
        
        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_relatives_extracting(self):
        data = {
                 "name": "Category 1",
                 "children": [
                     {
                         "name": "Category 1.1",
                         "children": [
                             {
                             "name": "Category 1.1.1",
                             "children": [
                                 {
                                 "name": "Category 1.1.1.1"
                                 },
                                 {
                                 "name": "Category 1.1.1.2"
                                 },
                                 {
                                 "name": "Category 1.1.1.3"
                                 }
                                ]
                             },
                             {
                             "name": "Category 1.1.2",
                             "children": [
                                 {
                                 "name": "Category 1.1.2.1"
                                 },
                                 {
                                 "name": "Category 1.1.2.2"
                                 },
                                 {
                                 "name": "Category 1.1.2.3"
                                 }
                             ]
                             }
                         ]
                     },
                     {
                     "name": "Category 1.2",
                     "children": [
                         {
                         "name": "Category 1.2.1"
                         },
                         {
                         "name": "Category 1.2.2",
                         "children": [
                                {
                                 "name": "Category 1.2.2.1"
                                 },
                                 {
                                 "name": "Category 1.2.2.2"
                                 }
                            ]
                        }
                     ]
                    }
                ]
            }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Now lets test if extraction is proper
        expected_data = {
         "id": 2,
         "name": "Category 1.1",
         "parents": [
             {
             "id": 1,
             "name": "Category 1"
             }
          ],
         "children": [
             {
             "id": 3,
             "name": "Category 1.1.1"
             },
             {
             "id": 7,
             "name": "Category 1.1.2"
             }
          ],
         "siblings": [
             {
             "id": 11,
             "name": "Category 1.2"
             }
          ]
        }
        extracted_data = self.client.get(reverse('category:categories-detail', [2])).data
        self.assertEqual(expected_data, extracted_data)

        expected_data = {
         "id": 8,
         "name": "Category 1.1.2.1",
         "parents": [
             {
             "id": 7,
             "name": "Category 1.1.2"
             },
             {
             "id": 2,
             "name": "Category 1.1"
             },
             {
             "id": 1,
             "name": "Category 1"
             },
          ],
         "children": [],
         "siblings": [
             {
             "id": 9,
             "name": "Category 1.1.2.2"
             },
             {
             "id": 10,
             "name": "Category 1.1.2.3"
             }
          ]
        }

        extracted_data = self.client.get(reverse('category:categories-detail', [8])).data
        self.assertEqual(expected_data, extracted_data)
