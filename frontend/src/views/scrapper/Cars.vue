<template>
  <div>
    <base-header type="gradient-success" class="pb-6 pb-8 pt-5 pt-md-8">
      <h3>seach</h3>
      <form class="form mr-3 d-md-flex ml-lg-auto">
        <div class="form-group mb-0">
          <input
            placeholder="Search"
            class="input-group-alternative form-control"
            alternative=""
            v-model="searchQuery"
            @input="onSearch"
            addon-right-icon="fas fa-search"
          />
        </div>
      </form>
      <div class="row"></div>
    </base-header>
    <div class="row px-3">
      <div
        class="card col-md-4 col-sm-12 mt-4 p-sm-2 p-4"
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
          <span class="detail">
            <a :href="row.website">{{ row.car_name }}</a>
          </span>
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
        <div class="name-detail">
          <span class="name" style="width: 150px"> Date: </span>
          <span class="detail"> {{ getDate(row.entry_date) }} </span>
        </div>
        <div class="my-1">
          <a
            :href="row.car_page_link"
            style="color: white; text-decoration: none"
          >
            <button type="button" class="btn btn-block btn-sm btn-info">
              details
            </button>
          </a>
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
      searchQuery: null,
      cars: [],
      allcars: [],
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
        this.allcars = this.cars;
        console.log(x["data"]);
      })
      .catch((e) => console.log(e));
  },
  methods: {
    getDate(date) {
      return new Date(date).toISOString();
    },

    onSearch() {
      console.log(this.searchQuery);
      if (this.searchQuery) {
        console.log("this.carss");
        this.cars = this.allcars.filter((item) => {
          return this.searchQuery
            .toLowerCase()
            .split(" ")
            .every((v) => {
              return item.car_name.toLowerCase().includes(v);
            });
        });
      } else {
        console.log("this.cars");
        return (this.cars = this.allcars);
      }
    },
  },
  computed: {
    resultQuery() {
      if (this.searchQuery) {
        console.log("this.carss");
        return this.cars.filter((item) => {
          return this.searchQuery
            .toLowerCase()
            .split(" ")
            .every((v) => {
              return item.car_name.toLowerCase().includes(v);
            });
        });
      } else {
        console.log("this.cars");
        return this.cars;
      }
    },
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

  width: 150px !important;
}
.detail {
  width: 70%;
  padding-left: 20px;
}
.name-detail {
  display: flex;
  justify-content: space-between;
  width: 100%;
  border-bottom: 1px solid rgba(128, 128, 128, 0.37);
  clear: both;
}
</style>
