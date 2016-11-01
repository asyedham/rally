#!/bin/sh

rand_int() {
    od -An -tu -N1 /dev/urandom | tr -d ' '
}

cat << EOF
{
  "additive": [
    {
      "title": "Statistics table from Hook",
      "chart_plugin": "StatsTable",
      "data": [
        ["Alice", $(rand_int)],
        ["Bob", $(rand_int)],
        ["Carol", $(rand_int)]]
    },
    {
      "title": "StackedArea chart from Hook",
      "description": "This is generated by ${0}",
      "chart_plugin": "StackedArea",
      "data": [
        ["Alpha", $(rand_int)],
        ["Beta", $(rand_int)],
        ["Gamma", $(rand_int)]]
    }
  ],
  "complete": [
    {
      "title": "Lines chart from Hook",
      "description": "Random data generated by ${0}",
      "chart_plugin": "Lines",
      "axis_label": "X-axis label",
      "label": "Y-axis label",
      "data": [
        ["Foo", [[1, $(rand_int)], [2, $(rand_int)], [3, $(rand_int)], [4, $(rand_int)], [5, $(rand_int)]]],
        ["Bar", [[1, $(rand_int)], [2, $(rand_int)], [3, $(rand_int)], [4, $(rand_int)], [5, $(rand_int)]]],
        ["Spam", [[1, $(rand_int)], [2, $(rand_int)], [3, $(rand_int)], [4, $(rand_int)], [5, $(rand_int)]]],
        ["Quiz", [[1, $(rand_int)], [2, $(rand_int)], [3, $(rand_int)], [4, $(rand_int)], [5, $(rand_int)]]]
      ]
    },
    {
      "title": "Pie chart from Hook",
      "description": "Yet another data generated by ${0}",
      "chart_plugin": "Pie",
      "data": [
        ["Cat", $(rand_int)],
        ["Tiger", $(rand_int)],
        ["Jaguar", $(rand_int)],
        ["Panther", $(rand_int)],
        ["Lynx", $(rand_int)]
      ]
    }
  ]
}
EOF