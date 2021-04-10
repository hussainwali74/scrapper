<template>
  <div>
    <base-header type="gradient-success" class="pb-6 pb-8 pt-5 pt-md-8">
      <div class="row"></div>
    </base-header>
    <div class="row">
      <div
        class="card col-md-3 col-sm-12 mt-4 p-sm-2 p-4"
        v-for="(row, index) in cars"
        :key="index"
      >
        <div>
          <img
            alt="Image placeholder"
            :src="row.img_link"
            class="img-thumbnail"
          />
        </div>
        <th scope="">{{ index }}</th>
        <div class="name-detail">
          <span class="name"> Name: </span>
          <span class="detail"> {{ row.car_name }} </span>
        </div>
        <div class="name-detail">
          <span class="name">Drive Train:</span>
          <span class="detail">
            {{ row.drivetrain }}
          </span>
        </div>
        <div class="name-detail">
          <span class="name">Engine:</span>
          <span class="detail">
            {{ row.engine }}
          </span>
        </div>

        <div class="name-detail">
          <span class="name"> Exterior: </span>
          <span class="detail">
            {{ row.exterior }}
          </span>
        </div>

        <div class="name-detail">
          <span class="name"> Mileage: </span>
          <span class="detail">
            {{ row.mileage }}
          </span>
        </div>

        <div class="name-detail">
          <span class="name"> Price: </span>
          <span class="detail"> ${{ row.price || 0 }} </span>
        </div>
      </div>
    </div>

    <div class="container-fluid">
      <div class="row">
        <div class="col">
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
                  <tr>
                    <th style="width: 10%">Name</th>
                    <th style="width: 5%">Drive</th>
                    <th style="width: 13%">Engine</th>
                    <th style="width: 5%">Exterior</th>
                    <th style="width: 5%">Mileage</th>
                    <th style="width: 5%">Price</th>
                    <th style="width: 20%"></th>
                  </tr>
                </template>
                <template v-slot:default="row">
                  <tr>
                    <td
                      class="pl-3"
                      style="
                        width: 100px;
                        overflow: hidden;
                        padding-left: 1.5rem !important;
                        background: #eee;
                      "
                    >
                      {{ row.item.car_name }} Lorem ipsum dolor sit amet
                      consectetur adipisicing elit. Assumenda asperiores dolorem
                      eius rem quia? Voluptate aspernatur atque quam expedita
                      itaque quos nostrum saepe illum totam, ad maxime ullam
                      numquam eveniet!
                    </td>
                    <td
                      style="width: 100px; overflow: hidden; background: #ee1"
                      class=""
                    >
                      {{ row.item.drivetrain }}
                    </td>
                    <td style="width: 100px" class="">
                      {{ row.item.engine }}
                    </td>
                    <td style="width: 100px" class="">
                      {{ row.item.exterior }}
                    </td>
                    <td style="width: 100px" class="">
                      {{ row.item.mileage }}
                    </td>
                    <td
                      class="text-bold"
                      style="width: 100px; font-weight: bold; color: #083d91bd"
                    >
                      ${{ row.item.price || 0 }}
                    </td>

                    <td style="width: 200px">
                      <img
                        alt="Image placeholder"
                        :src="row.item.img_link"
                        height="200"
                      />
                    </td>
                  </tr>
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
        this.cars.sort(function (a, b) {
          return new Date(b.entry_date) - new Date(a.entry_date);
        });
        console.log(x["data"]);
      })
      .catch((e) => console.log(e));
  },
};
</script>
<style scoped>
td {
  overflow: hidden !important;
}
.name {
  font-weight: bold;
  color: #083d91bd;
  background: rgb(255, 0, 0);
  width: 150px !important;
}
.detail {
  width: 70%;
  padding-left: 20px;
}
.name-detail {
  width: 100%;
}
</style>
