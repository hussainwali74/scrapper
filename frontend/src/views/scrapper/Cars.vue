<template>
  <div>
    <base-header type="gradient-success" class="pb-6 pb-8 pt-5 pt-md-8">
      <!-- Card stats -->
      <div class="row"></div>
    </base-header>

    <div class="container-fluid mt--7">
      <div class="row">
        <div class="col">
          <!-- <projects-table title="Light Table"></projects-table> -->
          <div class="card shadow" :class="type === 'dark' ? 'bg-default' : ''">
            <div
              class="card-header border-0"
              :class="type === 'dark' ? 'bg-transparent' : ''"
            >
              <div class="row align-items-center">
                <div class="col">
                  <h3 class="mb-0" :class="type === 'dark' ? 'text-white' : ''">
                    {{ title }}
                  </h3>
                </div>
                <div class="col text-right">
                  <base-button type="primary" size="sm">See all</base-button>
                </div>
              </div>
            </div>

            <div class="table-responsive">
              <base-table
                class="table align-items-center table-flush"
                :class="type === 'dark' ? 'table-dark' : ''"
                :thead-classes="type === 'dark' ? 'thead-dark' : 'thead-light'"
                tbody-classes="list"
                :data="cars"
              >
                <template v-slot:columns class="text-bold font-bold">
                  <th>Name</th>
                  <th>Drive</th>
                  <th>Engine</th>
                  <th>Exterior</th>
                  <th>Mileage</th>
                  <th>Price</th>
                  <th></th>
                </template>

                <template v-slot:default="row">
                  <th scope="row">
                    <div class="media align-items-center">
                      <div class="media-body">
                        <a :href="row.item.website">
                          <span class="name mb-0 text-sm">{{
                            row.item.car_name
                          }}</span>
                        </a>
                      </div>
                    </div>
                  </th>
                  <td class="">
                    {{ row.item.drivetrain }}
                  </td>
                  <td class="">
                    {{ row.item.engine }}
                  </td>

                  <td class="">
                    {{ row.item.exterior }}
                  </td>
                  <td class="">
                    {{ row.item.mileage }}
                  </td>
                  <td
                    class="text-bold"
                    style="font-weight: bold; color: #083d91bd"
                  >
                    ${{ row.item.price }}
                  </td>

                  <td>
                    <badge class="badge-dot mr-4" :type="row.item.statusType">
                      <i :class="`bg-${row.item.statusType}`"></i>
                      <span class="status">{{ row.item.status }}</span>
                    </badge>
                  </td>
                  <td>
                    <img
                      alt="Image placeholder"
                      :src="row.item.img_link"
                      height="200"
                    />
                  </td>
                </template>
              </base-table>
            </div>

            <div
              class="card-footer d-flex justify-content-end"
              :class="type === 'dark' ? 'bg-transparent' : ''"
            >
              <base-pagination total="30"></base-pagination>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import axios from "axios";
export default {
  name: "CarsComponent",

  props: {
    type: {
      type: String,
    },
    title: String,
  },
  data() {
    return {
      tableData: [
        {
          img: "img/theme/bootstrap.jpg",
          title: "Argon Design System",
          budget: "$2500 USD",
          status: "pending",
          statusType: "warning",
          completion: 60,
        },
        {
          img: "img/theme/angular.jpg",
          title: "Angular Now UI Kit PRO",
          budget: "$1800 USD",
          status: "completed",
          statusType: "success",
          completion: 100,
        },
        {
          img: "img/theme/sketch.jpg",
          title: "Black Dashboard",
          budget: "$3150 USD",
          status: "delayed",
          statusType: "danger",
          completion: 72,
        },
        {
          img: "img/theme/react.jpg",
          title: "React Material Dashboard",
          budget: "$4400 USD",
          status: "on schedule",
          statusType: "info",
          completion: 90,
        },
        {
          img: "img/theme/vue.jpg",
          title: "Vue Paper UI Kit PRO",
          budget: "$2200 USD",
          status: "completed",
          statusType: "success",
          completion: 100,
        },
      ],
      cars: [],
    };
  },
  created() {
    console.log("get h");
    // .get("http://localhost:8000/car/cars/")
    axios
      .get("https://car-scrapo.herokuapp.com/car/cars/?skip=0&limit=100")
      .then((x) => {
        this.cars = x["data"];
        console.log(x["data"]);
      })
      .catch((e) => console.log(e));
  },
};
</script>
<style></style>
